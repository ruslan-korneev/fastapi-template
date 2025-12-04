from sqlalchemy.ext.asyncio import AsyncSession


class FakeSessionMaker:
    """A session maker that returns the test session for transaction isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def __aenter__(self) -> AsyncSession:
        return self._session

    async def __aexit__(self, *args: object) -> None:
        pass
