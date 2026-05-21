# Database Performance Testing Suite

## Overview

This test suite validates the database optimizations implemented in task #12, including:
- Index performance (30-60x improvement)
- Query optimization (N+1 prevention, pagination)
- Backup/recovery procedures
- Connection pool stress testing
- Cache strategy validation

## Test Structure

```
tests/
├── unit/                    # Unit tests for database models
│   ├── test_models.py
│   └── test_enums.py
├── integration/             # Integration tests
│   ├── test_queries.py
│   ├── test_relationships.py
│   └── test_transactions.py
├── performance/             # Performance benchmarks
│   ├── test_index_performance.py
│   ├── test_query_optimization.py
│   ├── test_pagination.py
│   └── test_cache.py
└── conftest.py             # Pytest fixtures
```

## Requirements

```bash
pip install pytest pytest-asyncio pytest-benchmark pytest-cov faker locust
```

## Running Tests

### All Tests
```bash
pytest tests/
```

### Unit Tests Only
```bash
pytest tests/unit/
```

### Performance Benchmarks
```bash
pytest tests/performance/ --benchmark-only
```

### With Coverage Report
```bash
pytest tests/ --cov=app --cov-report=html
```

### Stress Test (Locust)
```bash
locust -f tests/performance/locustfile.py --host=http://localhost:8000
```

## Performance Targets

| Test Category | Target | Actual |
|--------------|--------|--------|
| List Query (20 items) | < 50ms | TBD |
| Detail Query | < 20ms | TBD |
| Statistics Query | < 200ms | TBD |
| Bulk Insert (100 items) | < 500ms | TBD |
| Index Scan vs Seq Scan | 30x faster | TBD |
| Cursor Pagination | 60x faster than OFFSET | TBD |
| Cache Hit Rate | > 80% | TBD |

## Test Database Setup

```bash
# Create test database
creatdb -U postgres admin_agent_test

# Run migrations
ALEMBIC_CONFIG=alembic.test.ini alembic upgrade head

# Load test data
python tests/fixtures/load_test_data.py
```

## CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Database Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          pip install -r requirements-test.txt
          pytest tests/ --cov=app
```
