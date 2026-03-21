from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

__all__ = ("router", "v1_router")

# Version 1 API router
# Add your module routers here, e.g.:
# from src.modules.users import router as users_router
# v1_router.include_router(users_router)
v1_router = APIRouter(prefix="/v1", route_class=DishkaRoute)


@v1_router.get("/health")
async def health_route(
    session: FromDishka[AsyncSession],
) -> dict[str, str]:
    """Check database connectivity."""
    await session.execute(text("SELECT 1"))
    return {"status": "healthy"}


# Main router includes all API versions
router = APIRouter()
router.include_router(v1_router)
