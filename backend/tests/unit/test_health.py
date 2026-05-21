"""Unit tests for health check endpoints"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
def test_health_check(client: TestClient):
    """
    Test basic health check endpoint
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "checks" in data


@pytest.mark.unit
def test_readiness_check(client: TestClient):
    """
    Test readiness probe endpoint
    """
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


@pytest.mark.unit
def test_liveness_check(client: TestClient):
    """
    Test liveness probe endpoint
    """
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"


@pytest.mark.unit
def test_metrics_endpoint(client: TestClient):
    """
    Test Prometheus metrics endpoint
    """
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "process_cpu_usage" in response.text
    assert "process_memory_usage" in response.text
