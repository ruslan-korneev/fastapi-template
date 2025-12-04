from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sentry_sdk import init as sentry_init
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.asyncpg import AsyncPGIntegration
from sentry_sdk.integrations.loguru import LoguruIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from starlette.middleware.cors import CORSMiddleware

from src.config import settings
from src.core.api import core_router
from src.core.dependencies.containers import Container
from src.core.exceptions import AppError
from src.core.middleware import InMemoryRateLimiter, RateLimitMiddleware, RequestIDMiddleware


class FastAPIWrapper(FastAPI):
    container: Container


def _get_request_id(request: Request) -> str | None:
    """Extract request ID from request state if available."""
    return getattr(request.state, "request_id", None)


def _build_error_response(
    error: str,
    detail: str,
    request_id: str | None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build consistent error response format."""
    response: dict[str, Any] = {
        "error": error,
        "detail": detail,
    }
    if request_id:
        response["request_id"] = request_id
    if extra:
        response["extra"] = extra
    return response


async def app_exception_handler(request: Request, exc: AppError) -> JSONResponse:
    """Handle custom application exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=_build_error_response(
            error=exc.__class__.__name__,
            detail=exc.detail,
            request_id=_get_request_id(request),
            extra=exc.extra if exc.extra else None,
        ),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors."""
    return JSONResponse(
        status_code=422,
        content=_build_error_response(
            error="ValidationError",
            detail="Request validation failed",
            request_id=_get_request_id(request),
            extra={"errors": exc.errors()},
        ),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:  # noqa: ARG001
    """Handle unexpected exceptions."""
    return JSONResponse(
        status_code=500,
        content=_build_error_response(
            error="InternalServerError",
            detail="An unexpected error occurred",
            request_id=_get_request_id(request),
        ),
    )


def get_app() -> FastAPIWrapper:
    container = Container()

    if sentry_dsn := settings.sentry.dsn.get_secret_value():
        sentry_init(
            dsn=sentry_dsn,
            environment=settings.environment,
            enable_tracing=settings.sentry.enable_tracing,
            traces_sample_rate=settings.sentry.traces_sample_rate,
            profiles_sample_rate=settings.sentry.profiles_sample_rate,
            integrations=[
                AsyncioIntegration(),
                AsyncPGIntegration(),
                LoguruIntegration(),
                SqlalchemyIntegration(),
            ],
        )

    app = FastAPIWrapper(
        title=settings.project_title,
        description=settings.project_description,
        version="2.0.0",
    )
    app.container = container

    # Register exception handlers
    app.add_exception_handler(AppError, app_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, generic_exception_handler)

    # Middleware order: last added runs first on request
    # 1. CORS (innermost - handles preflight)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.allow_origins,
        allow_origin_regex=settings.cors.allow_origin_regex,
        allow_credentials=settings.cors.allow_credentials,
        allow_methods=settings.cors.allow_methods,
        allow_headers=settings.cors.allow_headers,
        expose_headers=settings.cors.expose_headers,
        max_age=settings.cors.max_age,
    )

    # 2. Rate limiting (reject early if rate limited)
    if settings.rate_limit.enabled:
        limiter = InMemoryRateLimiter(
            requests_per_minute=settings.rate_limit.requests_per_minute,
            burst_size=settings.rate_limit.burst_size,
        )
        app.add_middleware(RateLimitMiddleware, limiter=limiter)

    # 3. Request ID (outermost - runs first, generates/tracks request IDs)
    app.add_middleware(RequestIDMiddleware)

    app.include_router(core_router)
    return app
