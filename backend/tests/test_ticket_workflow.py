"""Integration tests for ticket workflow."""

import pytest
from fastapi import status
from httpx import AsyncClient


class TestTicketWorkflow:
    """Test complete ticket workflow."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.db
    async def test_create_and_process_ticket(self, async_client: AsyncClient, test_user_data, test_admin_data, test_ticket_data):
        """Test creating and processing a ticket end-to-end."""
        # 1. Register employee and admin
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        await async_client.post("/api/v1/auth/register", json=test_admin_data)

        # 2. Employee login
        employee_login = await async_client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user_data["username"],
                "password": test_user_data["password"],
            },
        )
        employee_token = employee_login.json()["access_token"]

        # 3. Create ticket
        create_response = await async_client.post(
            "/api/v1/tickets",
            json=test_ticket_data,
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        ticket = create_response.json()
        ticket_id = ticket["id"]

        # 4. Admin login
        admin_login = await async_client.post(
            "/api/v1/auth/login",
            data={
                "username": test_admin_data["username"],
                "password": test_admin_data["password"],
            },
        )
        admin_token = admin_login.json()["access_token"]

        # 5. Admin assigns ticket to self
        assign_response = await async_client.patch(
            f"/api/v1/tickets/{ticket_id}/assign",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert assign_response.status_code == status.HTTP_200_OK

        # 6. Admin processes ticket
        process_response = await async_client.patch(
            f"/api/v1/tickets/{ticket_id}/status",
            json={"status": "processing"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert process_response.status_code == status.HTTP_200_OK

        # 7. Admin completes ticket
        complete_response = await async_client.patch(
            f"/api/v1/tickets/{ticket_id}/status",
            json={"status": "completed"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert complete_response.status_code == status.HTTP_200_OK

        # 8. Verify final ticket state
        get_response = await async_client.get(
            f"/api/v1/tickets/{ticket_id}",
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        final_ticket = get_response.json()
        assert final_ticket["processing_status"] == "completed"


    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_ticket_approval_workflow(self, async_client: AsyncClient, test_user_data, test_admin_data):
        """Test ticket requiring approval."""
        # Create high-value ticket requiring approval
        high_value_ticket = {
            "original_text": "需要采购100台电脑",
            "ticket_type": "procurement",
            "estimated_cost": 50000.00,  # High cost requiring approval
            "urgency": "high",
        }

        # Register users
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        await async_client.post("/api/v1/auth/register", json=test_admin_data)

        # Employee creates ticket
        employee_login = await async_client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user_data["username"],
                "password": test_user_data["password"],
            },
        )
        employee_token = employee_login.json()["access_token"]

        create_response = await async_client.post(
            "/api/v1/tickets",
            json=high_value_ticket,
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        ticket = create_response.json()

        # Verify ticket requires approval
        assert ticket["approval_status"] in ["pending_manager", "pending_finance"]

        # Admin approves
        admin_login = await async_client.post(
            "/api/v1/auth/login",
            data={
                "username": test_admin_data["username"],
                "password": test_admin_data["password"],
            },
        )
        admin_token = admin_login.json()["access_token"]

        approve_response = await async_client.post(
            f"/api/v1/tickets/{ticket['id']}/approve",
            json={"approved": True, "comment": "Approved"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert approve_response.status_code == status.HTTP_200_OK