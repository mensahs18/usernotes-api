import pytest
from sqlalchemy import create_engine
from database import Base
from dependencies import get_database
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from main import app

TEST_DB_URL = "sqlite:///./test.db"

test_engine = create_engine(TEST_DB_URL)
TestSession = sessionmaker(bind=test_engine)

@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    Base.metadata.create_all(test_engine)
    yield
    Base.metadata.drop_all(test_engine)

def get_test_database():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client():
    app.dependency_overrides[get_database] = get_test_database
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
