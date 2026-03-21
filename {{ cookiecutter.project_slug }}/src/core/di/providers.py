"""Dishka DI providers for the application.

AppProvider: Scope.APP -- singletons (Config).
RequestProvider: Scope.REQUEST -- per-request (AsyncSession).
"""

from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Config
from src.db.session import AsyncSessionMaker


class AppProvider(Provider):
    """Application-scoped dependencies (singletons)."""

    scope = Scope.APP

    @provide
    def config(self) -> Config:
        return Config()


class RequestProvider(Provider):
    """Request-scoped dependencies (per HTTP request)."""

    scope = Scope.REQUEST

    @provide
    async def session(self) -> AsyncIterator[AsyncSession]:
        async with AsyncSessionMaker() as session:
            yield session
