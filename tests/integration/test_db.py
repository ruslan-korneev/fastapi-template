from contextlib import suppress

from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession


async def test_db_health(session: AsyncSession) -> None:
    """Test database connectivity."""
    execution_succeeded = False
    with suppress(OperationalError, ConnectionRefusedError):
        await session.execute(text("SELECT 1"))
        execution_succeeded = True

    assert execution_succeeded
