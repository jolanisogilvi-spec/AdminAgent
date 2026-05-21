"""Unit tests for user authentication."""

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlmodel import Session


class TestUserRegistration:
    """Test user registration endpoints."""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_register_user_success(self, async_client: AsyncClient, test_user_data):
        """Test successful user registration."""
        response = await async_client.post("/api/v1/auth/register", json=test_user_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert "password" not in data  # Password should not be returned

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_register_duplicate_username(self, async_client: AsyncClient, test_user_data):
        """Test registration with duplicate username."""
        # Register first user
        await async_client.post("/api/v1/auth/register", json=test_user_data)

        # Try to register again with same username
        response = await async_client.post("/api/v1/auth/register", json=test_user_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_register_invalid_email(self, async_client: AsyncClient, test_user_data):
        """Test registration with invalid email."""
        test_user_data["email"] = "invalid-email"
        response = await async_client.post("/api/v1/auth/register", json=test_user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUserLogin:
    """Test user login endpoints."""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_login_success(self, async_client: AsyncClient, test_user_data):
        """Test successful login."""
        # Register user first
        await async_client.post("/api/v1/auth/register", json=test_user_data)

        # Login
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"],
        }
        response = await async_client.post("/api/v1/auth/login", data=login_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_login_wrong_password(self, async_client: AsyncClient, test_user_data):
        """Test login with wrong password."""
        # Register user first
        await async_client.post("/api/v1/auth/register", json=test_user_data)

        # Login with wrong password
        login_data = {
            "username": test_user_data["username"],
            "password": "wrongpassword",
        }
        response = await async_client.post("/api/v1/auth/login", data=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_login_nonexistent_user(self, async_client: AsyncClient):
        """Test login with non-existent user."""
        login_data = {
            "username": "nonexistent",
            "password": "password123",
        }
        response = await async_client.post("/api/v1/auth/login", data=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestProtectedEndpoints:
    """Test protected endpoints requiring authentication."""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_access_protected_endpoint_without_token(self, async_client: AsyncClient):
        """Test accessing protected endpoint without token."""
        response = await async_client.get("/api/v1/users/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_access_protected_endpoint_with_token(self, async_client: AsyncClient, test_user_data):
        """Test accessing protected endpoint with valid token."""
        # Register and login
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user_data["username"],
                "password": test_user_data["password"],
            },
        )
        token = login_response.json()["access_token"]

        # Access protected endpoint
        response = await async_client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == test_user_data["username"]