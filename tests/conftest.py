import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from database import Base
from dependencies import get_database
from httpx import AsyncClient, ASGITransport
from main import app

TEST_DB_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(TEST_DB_URL)
TestSession = async_sessionmaker(bind=test_engine)

@pytest.fixture(autouse=True)
async def setup_and_teardown_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

async def get_test_database():
    async with TestSession() as db:
        yield db

@pytest.fixture
async def client():
    app.dependency_overrides[get_database] = get_test_database
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()
