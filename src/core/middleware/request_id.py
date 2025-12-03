import uuid

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

__all__ = ("REQUEST_ID_HEADER", "RequestIDMiddleware")

REQUEST_ID_HEADER = "X-Request-ID"


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to generate and track request IDs.

    - Extracts request ID from incoming header or generates a new UUID
    - Stores the ID in request.state for access in handlers
    - Binds the ID to loguru context for automatic inclusion in logs
    - Adds the ID to response headers
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Get existing request ID from header or generate new one
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())

        # Store in request state for access in handlers and exception handlers
        request.state.request_id = request_id

        # Bind to loguru context for automatic inclusion in all logs
        with logger.contextualize(request_id=request_id):
            response = await call_next(request)

        # Add request ID to response headers
        response.headers[REQUEST_ID_HEADER] = request_id
        return response
