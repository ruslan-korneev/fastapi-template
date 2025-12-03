from sqlalchemy import text

from src.db.session import AsyncSessionMaker


async def test_async_session_maker() -> None:
    """Test that AsyncSessionMaker can open and close a session."""
    session_maker = AsyncSessionMaker()

    async with session_maker as session:
        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1
