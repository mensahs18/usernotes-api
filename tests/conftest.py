import os

import pytest
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from database import Base
from dependencies import get_database
from main import app

load_dotenv()
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    raise ValueError("'TEST_DATABASE_URL' environment variable is not set.")

TEST_DB_URL: str = TEST_DATABASE_URL

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
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()
