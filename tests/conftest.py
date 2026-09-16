import sys
from pathlib import Path

import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)
from sqlalchemy.pool import StaticPool

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent)
)

from models import Base
from main import app, get_db


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    expire_on_commit=False,
    class_=AsyncSession
)


@pytest_asyncio.fixture
async def test_db():
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def override_get_db(test_db):
    async def _override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = _override_get_db

    yield

    app.dependency_overrides.clear()