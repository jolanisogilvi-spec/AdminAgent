"""Unit tests for asset management."""

import pytest
from fastapi import status
from httpx import AsyncClient


class TestAssetCRUD:
    """Test asset CRUD operations."""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_create_asset(self, async_client: AsyncClient, test_admin_data, test_asset_data):
        """Test creating an asset."""
        # Register and login as admin
        await async_client.post("/api/v1/auth/register", json=test_admin_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            data={
                "username": test_admin_data["username"],
                "password": test_admin_data["password"],
            },
        )
        token = login_response.json()["access_token"]

        # Create asset
        response = await async_client.post(
            "/api/v1/assets",
            json=test_asset_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["asset_code"] == test_asset_data["asset_code"]
        assert data["name"] == test_asset_data["name"]

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_list_assets(self, async_client: AsyncClient, test_admin_data, test_asset_data):
        """Test listing assets."""
        # Setup
        await async_client.post("/api/v1/auth/register", json=test_admin_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            data={
                "username": test_admin_data["username"],
                "password": test_admin_data["password"],
            },
        )
        token = login_response.json()["access_token"]

        # Create multiple assets
        await async_client.post(
            "/api/v1/assets",
            json=test_asset_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        asset_data_2 = test_asset_data.copy()
        asset_data_2["asset_code"] = "MOUSE-002"
        await async_client.post(
            "/api/v1/assets",
            json=asset_data_2,
            headers={"Authorization": f"Bearer {token}"},
        )

        # List assets
        response = await async_client.get(
            "/api/v1/assets",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 2

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_update_asset_status(self, async_client: AsyncClient, test_admin_data, test_asset_data):
        """Test updating asset status."""
        # Setup
        await async_client.post("/api/v1/auth/register", json=test_admin_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            data={
                "username": test_admin_data["username"],
                "password": test_admin_data["password"],
            },
        )
        token = login_response.json()["access_token"]

        # Create asset
        create_response = await async_client.post(
            "/api/v1/assets",
            json=test_asset_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        asset_id = create_response.json()["id"]

        # Update status
        response = await async_client.patch(
            f"/api/v1/assets/{asset_id}",
            json={"status": "in_use"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "in_use"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_delete_asset(self, async_client: AsyncClient, test_admin_data, test_asset_data):
        """Test deleting an asset."""
        # Setup
        await async_client.post("/api/v1/auth/register", json=test_admin_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            data={
                "username": test_admin_data["username"],
                "password": test_admin_data["password"],
            },
        )
        token = login_response.json()["access_token"]

        # Create asset
        create_response = await async_client.post(
            "/api/v1/assets",
            json=test_asset_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        asset_id = create_response.json()["id"]

        # Delete asset
        response = await async_client.delete(
            f"/api/v1/assets/{asset_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deletion
        get_response = await async_client.get(
            f"/api/v1/assets/{asset_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND