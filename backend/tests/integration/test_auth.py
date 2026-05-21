"""Integration tests for user authentication"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
@pytest.mark.db
class TestUserAuthentication:
    """Test user registration and authentication flow"""

    def test_user_registration(self, client: TestClient, mock_user_data):
        """
        Test user registration endpoint
        """
        response = client.post("/api/v1/auth/register", json=mock_user_data)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["username"] == mock_user_data["username"]
        assert "password" not in data  # Password should not be returned

    def test_duplicate_username(self, client: TestClient, mock_user_data):
        """
        Test registration with duplicate username
        """
        # Register first user
        client.post("/api/v1/auth/register", json=mock_user_data)

        # Try to register again with same username
        response = client.post("/api/v1/auth/register", json=mock_user_data)
        assert response.status_code == 400

    def test_user_login(self, client: TestClient, mock_user_data):
        """
        Test user login endpoint
        """
        # Register user first
        client.post("/api/v1/auth/register", json=mock_user_data)

        # Login
        login_data = {
            "username": mock_user_data["username"],
            "password": mock_user_data["password"]
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client: TestClient, mock_user_data):
        """
        Test login with invalid credentials
        """
        login_data = {
            "username": mock_user_data["username"],
            "password": "wrong_password"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 401

    def test_protected_endpoint_without_token(self, client: TestClient):
        """
        Test accessing protected endpoint without authentication
        """
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401

    def test_protected_endpoint_with_token(self, client: TestClient, auth_headers):
        """
        Test accessing protected endpoint with valid token
        """
        response = client.get("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "username" in data
