"""Test configuration and fixtures."""

import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

# Set test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["REDIS_HOST"] = "localhost"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["JWT_SECRET_KEY"] = "test-jwt-secret-key"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(name="engine")
def engine_fixture():
    """Create test database engine."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="session")
def session_fixture(engine) -> Generator[Session, None, None]:
    """Create test database session."""
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """Create test client with database session override."""
    from app.main import app
    from app.core.database import get_session

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client(session: Session) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client."""
    from app.main import app
    from app.core.database import get_session

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {
        "username": "testuser",
        "full_name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123",
        "role": "employee",
        "department": "IT",
    }


@pytest.fixture
def test_admin_data():
    """Sample admin user data for testing."""
    return {
        "username": "admin",
        "full_name": "Admin User",
        "email": "admin@example.com",
        "password": "adminpassword123",
        "role": "sys_admin",
        "department": "Management",
    }


@pytest.fixture
def test_ticket_data():
    """Sample ticket data for testing."""
    return {
        "original_text": "需要采购10个鼠标",
        "ticket_type": "procurement",
        "estimated_cost": 500.00,
        "urgency": "normal",
    }


@pytest.fixture
def test_asset_data():
    """Sample asset data for testing."""
    return {
        "asset_code": "MOUSE-001",
        "name": "罗技鼠标",
        "category": "it_equipment",
        "status": "available",
        "unit_price": 50.00,
    }