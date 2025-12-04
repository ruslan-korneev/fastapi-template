from types import TracebackType

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings


class AsyncSessionMaker:
    _engine = create_async_engine(
        url=settings.db.get_url().get_secret_value(),
        future=True,
        pool_pre_ping=True,
        pool_size=8,
        max_overflow=4,
        pool_timeout=10,
        pool_recycle=300,
    )
    _sessionmaker = async_sessionmaker(
        bind=_engine,
        autoflush=False,
        autocommit=False,
    )

    def __init__(self) -> None:
        self._session = self._sessionmaker()

    async def __aenter__(self) -> AsyncSession:
        logger.debug("open db session")
        return await self._session.__aenter__()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        logger.debug("close db session")
        return await self._session.__aexit__(exc_type, exc_value, traceback)
