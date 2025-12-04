import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

if TYPE_CHECKING:
    from starlette.types import ASGIApp

__all__ = ("InMemoryRateLimiter", "RateLimitMiddleware")


@dataclass
class RateLimitBucket:
    """Token bucket for rate limiting a single client."""

    tokens: float
    last_update: float


class InMemoryRateLimiter:
    """Thread-safe in-memory rate limiter using token bucket algorithm.

    The token bucket algorithm allows for burst traffic while maintaining
    an average rate limit over time.
    """

    def __init__(self, requests_per_minute: int, burst_size: int) -> None:
        self.rate = requests_per_minute / 60.0  # tokens per second
        self.burst_size = burst_size
        self._buckets: dict[str, RateLimitBucket] = {}

    def is_allowed(self, key: str) -> tuple[bool, dict[str, str]]:
        """Check if request is allowed for the given key.

        Returns:
            Tuple of (is_allowed, headers_dict)
        """
        now = time.monotonic()

        if key not in self._buckets:
            # First request from this client
            self._buckets[key] = RateLimitBucket(
                tokens=self.burst_size - 1,
                last_update=now,
            )
            return True, self._get_headers(self.burst_size - 1)

        bucket = self._buckets[key]

        # Replenish tokens based on elapsed time
        elapsed = now - bucket.last_update
        bucket.tokens = min(self.burst_size, bucket.tokens + elapsed * self.rate)
        bucket.last_update = now

        if bucket.tokens >= 1:
            bucket.tokens -= 1
            return True, self._get_headers(bucket.tokens)

        # Rate limited - calculate retry time
        retry_after = int((1 - bucket.tokens) / self.rate) + 1
        headers = self._get_headers(bucket.tokens)
        headers["Retry-After"] = str(retry_after)
        return False, headers

    def _get_headers(self, remaining: float) -> dict[str, str]:
        """Build rate limit headers."""
        return {
            "X-RateLimit-Limit": str(self.burst_size),
            "X-RateLimit-Remaining": str(max(0, int(remaining))),
        }


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using token bucket algorithm."""

    # Paths to exclude from rate limiting
    EXCLUDED_PATHS: frozenset[str] = frozenset({"/health", "/v1/health"})

    def __init__(self, app: "ASGIApp", limiter: InMemoryRateLimiter) -> None:
        super().__init__(app)
        self.limiter = limiter

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Skip rate limiting for health checks
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)

        # Get client IP (support for proxied requests)
        client_ip = self._get_client_ip(request)

        allowed, headers = self.limiter.is_allowed(client_ip)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "RateLimitExceededError",
                    "detail": "Too many requests. Please retry later.",
                    "request_id": getattr(request.state, "request_id", None),
                },
                headers=headers,
            )

        response = await call_next(request)

        # Add rate limit headers to successful responses
        for key, value in headers.items():
            response.headers[key] = value

        return response

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        """Extract client IP, considering proxy headers."""
        # Check X-Forwarded-For header (common for proxied requests)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Take the first IP (original client)
            return forwarded.split(",")[0].strip()

        # Check X-Real-IP header (nginx)
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

        # Fall back to direct client IP
        if request.client:
            return request.client.host

        return "unknown"
