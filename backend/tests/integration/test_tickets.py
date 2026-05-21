"""Integration tests for ticket management"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
@pytest.mark.db
class TestTicketManagement:
    """Test ticket CRUD operations"""

    def test_create_ticket(self, client: TestClient, auth_headers, mock_ticket_data):
        """
        Test creating a new ticket
        """
        response = client.post(
            "/api/v1/tickets",
            json=mock_ticket_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["original_text"] == mock_ticket_data["original_text"]
        assert data["ticket_type"] == mock_ticket_data["ticket_type"]

    def test_list_tickets(self, client: TestClient, auth_headers, mock_ticket_data):
        """
        Test listing tickets
        """
        # Create a ticket first
        client.post("/api/v1/tickets", json=mock_ticket_data, headers=auth_headers)

        # List tickets
        response = client.get("/api/v1/tickets", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_ticket_by_id(self, client: TestClient, auth_headers, mock_ticket_data):
        """
        Test retrieving a specific ticket
        """
        # Create ticket
        create_response = client.post(
            "/api/v1/tickets",
            json=mock_ticket_data,
            headers=auth_headers
        )
        ticket_id = create_response.json()["id"]

        # Get ticket
        response = client.get(f"/api/v1/tickets/{ticket_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == ticket_id

    def test_update_ticket(self, client: TestClient, auth_headers, mock_ticket_data):
        """
        Test updating a ticket
        """
        # Create ticket
        create_response = client.post(
            "/api/v1/tickets",
            json=mock_ticket_data,
            headers=auth_headers
        )
        ticket_id = create_response.json()["id"]

        # Update ticket
        update_data = {"processing_status": "处理中"}
        response = client.patch(
            f"/api/v1/tickets/{ticket_id}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["processing_status"] == "处理中"

    def test_delete_ticket(self, client: TestClient, auth_headers, mock_ticket_data):
        """
        Test deleting a ticket
        """
        # Create ticket
        create_response = client.post(
            "/api/v1/tickets",
            json=mock_ticket_data,
            headers=auth_headers
        )
        ticket_id = create_response.json()["id"]

        # Delete ticket
        response = client.delete(f"/api/v1/tickets/{ticket_id}", headers=auth_headers)
        assert response.status_code == 200

        # Verify deletion
        get_response = client.get(f"/api/v1/tickets/{ticket_id}", headers=auth_headers)
        assert get_response.status_code == 404
