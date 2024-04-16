import pytest
from src.conf.config import config
from src.database.db import DatabaseSessionManager


@pytest.fixture
async def session_manager():
    db_url = config.DB_URL
    session_manager = DatabaseSessionManager(db_url)
    yield session_manager
    if session_manager.engine:
        await session_manager._engine.dispose()


@pytest.mark.asyncio
async def test_session_manager(session_manager):
    async for session in session_manager:
        assert session is not None


@pytest.mark.asyncio
async def test_rollback(session_manager):
    with pytest.raises(Exception):
        async with session_manager.session() as session:
            raise Exception("Simulated error")

