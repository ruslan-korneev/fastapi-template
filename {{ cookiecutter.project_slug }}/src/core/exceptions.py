from typing import Any

from fastapi import status

__all__ = (
    "AppError",
    "ConflictError",
    "NotFoundError",
    "RateLimitExceededError",
    "ValidationError",
)


class AppError(Exception):
    """Base application exception with HTTP status code."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "Internal server error"

    def __init__(self, detail: str | None = None, **kwargs: Any) -> None:
        self.detail = detail or self.__class__.detail
        self.extra = kwargs
        super().__init__(self.detail)


class NotFoundError(AppError):
    """Resource not found exception."""

    status_code = status.HTTP_404_NOT_FOUND
    detail = "Resource not found"


class ConflictError(AppError):
    """Resource conflict exception (e.g., duplicate)."""

    status_code = status.HTTP_409_CONFLICT
    detail = "Resource already exists"


class ValidationError(AppError):
    """Validation error exception."""

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Validation error"


class RateLimitExceededError(AppError):
    """Rate limit exceeded exception."""

    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    detail = "Rate limit exceeded"
