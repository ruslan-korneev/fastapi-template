from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from sqlalchemy import text

from src.core.dependencies.containers import Container
from src.db.session import AsyncSessionMaker
from src.modules.users import router as users_router

__all__ = ("router", "v1_router")

# Version 1 API router
v1_router = APIRouter(prefix="/v1")
v1_router.include_router(users_router)


@v1_router.get("/health")
@inject
async def health_route(
    db_session_maker: Annotated[AsyncSessionMaker, Depends(Provide[Container.db_session_maker])],
) -> dict[str, str]:
    """Check database connectivity."""
    async with db_session_maker as session:
        await session.execute(text("SELECT 1"))
    return {"status": "healthy"}


# Main router includes all API versions
router = APIRouter()
router.include_router(v1_router)
