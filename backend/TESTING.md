# Testing Guide

## Overview

This project uses pytest for testing with comprehensive coverage reporting and CI/CD integration.

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Unit tests
│   ├── test_health.py      # Health check tests
│   ├── test_models.py      # Model tests
│   └── test_services.py    # Service layer tests
├── integration/             # Integration tests
│   ├── test_auth.py        # Authentication flow tests
│   ├── test_tickets.py     # Ticket management tests
│   └── test_assets.py      # Asset management tests
└── fixtures/                # Test data and utilities
```

## Running Tests

### Quick Start

```bash
# Run all tests
./run_tests.sh

# Run specific test file
pytest tests/unit/test_health.py

# Run tests with specific marker
pytest -m unit
pytest -m integration
pytest -m "not slow"

# Run tests with coverage
pytest --cov=app --cov-report=html
```

### Test Markers

- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (require database)
- `@pytest.mark.slow` - Slow running tests
- `@pytest.mark.db` - Tests requiring database
- `@pytest.mark.redis` - Tests requiring Redis

## Test Environment

### Local Testing

```bash
# Start test databases
docker-compose -f docker-compose.test.yml up -d

# Run tests
pytest

# Stop test databases
docker-compose -f docker-compose.test.yml down -v
```

### Environment Variables

Test environment variables are configured in `pyproject.toml`:

```toml
env = [
    "TESTING=true",
    "DATABASE_URL=postgresql://test:test@localhost:5433/test_admin_agent",
    "REDIS_URL=redis://localhost:6380/0",
]
```

## Fixtures

### Database Fixtures

```python
def test_example(session: Session):
    # session fixture provides database session
    pass
```

### Client Fixture

```python
def test_api_endpoint(client: TestClient):
    response = client.get("/api/v1/endpoint")
    assert response.status_code == 200
```

### Authentication Fixture

```python
def test_protected_endpoint(client: TestClient, auth_headers):
    response = client.get("/api/v1/protected", headers=auth_headers)
    assert response.status_code == 200
```

### Mock Data Fixtures

```python
def test_create_user(client: TestClient, mock_user_data):
    response = client.post("/api/v1/users", json=mock_user_data)
    assert response.status_code == 200
```

## Coverage Reports

### Viewing Coverage

```bash
# Terminal report
pytest --cov=app --cov-report=term-missing

# HTML report (opens in browser)
pytest --cov=app --cov-report=html
open htmlcov/index.html

# XML report (for CI/CD)
pytest --cov=app --cov-report=xml
```

### Coverage Goals

- **Minimum**: 80% overall coverage
- **Target**: 90% overall coverage
- **Critical paths**: 100% coverage (auth, payments, data integrity)

## Writing Tests

### Unit Test Example

```python
import pytest
from app.services.ticket_service import TicketService

@pytest.mark.unit
def test_ticket_validation():
    """Test ticket data validation"""
    service = TicketService()
    
    # Test valid data
    valid_data = {"original_text": "Need laptop", "ticket_type": "purchase"}
    assert service.validate(valid_data) is True
    
    # Test invalid data
    invalid_data = {"original_text": "", "ticket_type": "invalid"}
    with pytest.raises(ValueError):
        service.validate(invalid_data)
```

### Integration Test Example

```python
import pytest
from fastapi.testclient import TestClient

@pytest.mark.integration
@pytest.mark.db
def test_ticket_workflow(client: TestClient, auth_headers, mock_ticket_data):
    """Test complete ticket creation and approval workflow"""
    # Create ticket
    response = client.post(
        "/api/v1/tickets",
        json=mock_ticket_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    ticket_id = response.json()["id"]
    
    # Approve ticket
    response = client.post(
        f"/api/v1/tickets/{ticket_id}/approve",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["approval_status"] == "已通过"
```

## CI/CD Integration

Tests are automatically run in GitHub Actions on:
- Pull requests
- Pushes to main/develop branches

See `.github/workflows/ci-cd.yml` for configuration.

### CI Test Commands

```yaml
- name: Run tests
  run: |
    pytest tests/ \
      --cov=app \
      --cov-report=xml \
      --cov-report=term

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## Best Practices

### 1. Test Isolation

- Each test should be independent
- Use fixtures for setup/teardown
- Don't rely on test execution order

### 2. Test Naming

```python
def test_<feature>_<scenario>_<expected_result>():
    # Example: test_user_login_with_invalid_password_returns_401
    pass
```

### 3. Arrange-Act-Assert Pattern

```python
def test_example():
    # Arrange
    user_data = {"username": "test", "password": "pass"}
    
    # Act
    response = client.post("/api/v1/auth/login", json=user_data)
    
    # Assert
    assert response.status_code == 200
```

### 4. Mock External Services

```python
from unittest.mock import patch

@patch('app.services.ai_service.OpenAI')
def test_ai_integration(mock_openai):
    mock_openai.return_value.chat.completions.create.return_value = {
        "choices": [{"message": {"content": "Test response"}}]
    }
    # Test code here
```

### 5. Test Data Management

- Use Faker for realistic test data
- Create reusable fixtures
- Clean up after tests

## Debugging Tests

```bash
# Run with verbose output
pytest -vv

# Stop on first failure
pytest -x

# Run specific test
pytest tests/unit/test_health.py::test_health_check

# Show print statements
pytest -s

# Debug with pdb
pytest --pdb
```

## Performance Testing

```python
import pytest

@pytest.mark.slow
def test_bulk_ticket_creation(client: TestClient, auth_headers):
    """Test creating 1000 tickets"""
    import time
    start = time.time()
    
    for i in range(1000):
        client.post("/api/v1/tickets", json={...}, headers=auth_headers)
    
    duration = time.time() - start
    assert duration < 10  # Should complete in under 10 seconds
```

## Troubleshooting

### Database Connection Issues

```bash
# Check if test database is running
docker-compose -f docker-compose.test.yml ps

# View database logs
docker-compose -f docker-compose.test.yml logs test-postgres

# Reset test database
docker-compose -f docker-compose.test.yml down -v
docker-compose -f docker-compose.test.yml up -d
```

### Import Errors

```bash
# Ensure you're in the backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Set PYTHONPATH
export PYTHONPATH=$PWD
```

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [Faker Documentation](https://faker.readthedocs.io/)
