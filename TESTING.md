# Testing Infrastructure Guide

## Overview

Comprehensive testing setup for the Admin Agent project with both backend (FastAPI/Python) and frontend (React/TypeScript) testing frameworks.

## Backend Testing (Python/FastAPI)

### Setup

1. **Install test dependencies:**
   ```bash
   cd backend
   pip install -r requirements-test.txt
   ```

2. **Run tests:**
   ```bash
   # Run all tests
   pytest

   # Run with coverage
   pytest --cov=app --cov-report=html

   # Run specific test file
   pytest tests/test_auth.py

   # Run specific test class
   pytest tests/test_auth.py::TestUserLogin

   # Run specific test
   pytest tests/test_auth.py::TestUserLogin::test_login_success

   # Run tests with markers
   pytest -m unit          # Only unit tests
   pytest -m integration   # Only integration tests
   pytest -m "not slow"    # Exclude slow tests
   ```

### Test Structure

```
backend/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Shared fixtures
│   ├── test_config.py           # Configuration tests
│   ├── test_auth.py             # Authentication tests
│   ├── test_assets.py           # Asset management tests
│   └── test_ticket_workflow.py  # Integration tests
├── pyproject.toml               # Pytest configuration
└── requirements-test.txt        # Test dependencies
```

### Test Categories

#### 1. Unit Tests (`@pytest.mark.unit`)
- Test individual functions/methods in isolation
- Mock external dependencies
- Fast execution
- Examples: `test_auth.py`, `test_assets.py`

#### 2. Integration Tests (`@pytest.mark.integration`)
- Test complete workflows
- Use test database
- Test API endpoints end-to-end
- Examples: `test_ticket_workflow.py`

#### 3. Database Tests (`@pytest.mark.db`)
- Require database connection
- Use SQLite in-memory for speed
- Automatic cleanup after each test

### Key Features

**Fixtures (conftest.py):**
- `engine`: Test database engine
- `session`: Database session
- `client`: Synchronous test client
- `async_client`: Asynchronous test client
- `test_user_data`: Sample user data
- `test_admin_data`: Sample admin data
- `test_ticket_data`: Sample ticket data
- `test_asset_data`: Sample asset data

**Configuration (pyproject.toml):**
- Coverage thresholds: 80%
- Async test support
- HTML/XML coverage reports
- Code quality tools (ruff, black, mypy)

### Writing Tests

**Example Unit Test:**
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
@pytest.mark.unit
async def test_create_user(async_client: AsyncClient, test_user_data):
    response = await async_client.post("/api/v1/users", json=test_user_data)
    assert response.status_code == 201
    assert response.json()["username"] == test_user_data["username"]
```

**Example Integration Test:**
```python
@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.db
async def test_ticket_workflow(async_client, test_user_data, test_admin_data):
    # Multi-step workflow test
    # 1. Register users
    # 2. Create ticket
    # 3. Process ticket
    # 4. Verify final state
```

### Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=app --cov-report=html

# View report
open htmlcov/index.html

# Generate XML for CI/CD
pytest --cov=app --cov-report=xml
```

## Frontend Testing (React/TypeScript)

### Setup

1. **Install dependencies** (already included):
   ```bash
   cd frontend
   npm install
   ```

2. **Run tests:**
   ```bash
   # Run all tests
   npm test

   # Run with coverage
   npm test -- --coverage

   # Run in watch mode
   npm test -- --watch

   # Run specific test file
   npm test -- Login.test.tsx

   # Run with UI
   npm test -- --ui
   ```

### Test Structure

```
frontend/
├── src/
│   ├── __tests__/
│   │   ├── Login.test.tsx       # Component tests
│   │   ├── api.test.ts          # API hook tests
│   │   ├── stores.test.ts       # Zustand store tests
│   │   └── utils.test.ts        # Utility function tests
│   └── test/
│       └── setup.ts             # Test setup & mocks
├── vitest.config.ts             # Vitest configuration
└── package.json                 # Test scripts
```

### Test Categories

#### 1. Component Tests
- Render components
- User interactions
- State changes
- Props validation

#### 2. Hook Tests
- React Query hooks
- Custom hooks
- API integration

#### 3. Store Tests
- Zustand state management
- Actions and reducers
- State persistence

#### 4. Utility Tests
- Pure functions
- Helpers
- Constants

### Writing Tests

**Example Component Test:**
```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Login } from './Login';

it('submits login form', async () => {
  const user = userEvent.setup();
  render(<Login />);

  await user.type(screen.getByLabelText(/username/i), 'testuser');
  await user.type(screen.getByLabelText(/password/i), 'password123');
  await user.click(screen.getByRole('button', { name: /login/i }));

  expect(screen.getByText(/welcome/i)).toBeInTheDocument();
});
```

**Example Hook Test:**
```typescript
import { renderHook, waitFor } from '@testing-library/react';
import { useTickets } from './hooks/useTickets';

it('fetches tickets', async () => {
  const { result } = renderHook(() => useTickets(), {
    wrapper: createWrapper(),
  });

  await waitFor(() => expect(result.current.isSuccess).toBe(true));
  expect(result.current.data).toHaveLength(2);
});
```

### Coverage Configuration

**vitest.config.ts** sets coverage thresholds:
- Lines: 80%
- Functions: 80%
- Branches: 80%
- Statements: 80%

## CI/CD Integration

Tests are automatically run in GitHub Actions (`.github/workflows/ci-cd.yml`):

### Backend CI
```yaml
- Run linting (ruff)
- Run tests (pytest)
- Upload coverage to Codecov
```

### Frontend CI
```yaml
- Run linting (ESLint)
- Type checking (TypeScript)
- Run tests (Vitest)
- Build validation
```

## Best Practices

### Backend
1. **Use fixtures** for common test data
2. **Mark tests appropriately** (unit/integration/slow/db)
3. **Test both success and failure cases**
4. **Use async/await** for async tests
5. **Mock external services** (OpenAI API, email, etc.)
6. **Clean up after tests** (automatic with fixtures)

### Frontend
1. **Test user behavior**, not implementation
2. **Use semantic queries** (getByRole, getByLabelText)
3. **Mock API calls** to avoid network requests
4. **Test accessibility** (ARIA labels, keyboard navigation)
5. **Keep tests focused** (one assertion per test when possible)
6. **Use Testing Library best practices**

## Test Data

### Backend Fixtures
```python
test_user_data = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123",
    "role": "employee",
}

test_ticket_data = {
    "original_text": "需要采购10个鼠标",
    "ticket_type": "procurement",
    "estimated_cost": 500.00,
}
```

### Frontend Mocks
```typescript
const mockUser = {
  id: 1,
  username: 'testuser',
  role: 'employee',
};

const mockTicket = {
  id: 1,
  original_text: '需要采购鼠标',
  status: 'pending',
};
```

## Debugging Tests

### Backend
```bash
# Run with verbose output
pytest -vv

# Run with print statements
pytest -s

# Run with debugger
pytest --pdb

# Run last failed tests
pytest --lf
```

### Frontend
```bash
# Run with UI debugger
npm test -- --ui

# Run with browser
npm test -- --browser

# Debug specific test
npm test -- --reporter=verbose Login.test.tsx
```

## Performance

### Backend
- Use SQLite in-memory for speed
- Parallel test execution: `pytest -n auto`
- Skip slow tests in development: `pytest -m "not slow"`

### Frontend
- Tests run in parallel by default
- Use `vi.mock()` to avoid heavy imports
- Lazy load test utilities

## Continuous Improvement

1. **Monitor coverage trends** in CI/CD
2. **Add tests for new features** before merging
3. **Refactor tests** when they become brittle
4. **Update fixtures** as models evolve
5. **Review test failures** in CI - don't ignore them

## Quick Reference

### Backend Commands
```bash
pytest                          # Run all tests
pytest -m unit                  # Unit tests only
pytest --cov                    # With coverage
pytest -k "test_login"          # Tests matching pattern
pytest --lf                     # Last failed
```

### Frontend Commands
```bash
npm test                        # Run all tests
npm test -- --coverage          # With coverage
npm test -- --watch             # Watch mode
npm test -- --ui                # UI mode
npm test -- Login.test.tsx      # Specific file
```

## Troubleshooting

### Backend
**Issue:** Tests fail with database errors
**Solution:** Check `conftest.py` fixtures, ensure SQLModel metadata is created

**Issue:** Async tests hang
**Solution:** Verify `pytest-asyncio` is installed, use `@pytest.mark.asyncio`

### Frontend
**Issue:** "Cannot find module" errors
**Solution:** Check `vitest.config.ts` alias configuration

**Issue:** Tests timeout
**Solution:** Increase timeout in `vitest.config.ts` or use `waitFor` with longer timeout

## Next Steps

1. ✅ Test infrastructure set up
2. ⏳ Write tests for existing features
3. ⏳ Achieve 80%+ coverage
4. ⏳ Set up mutation testing
5. ⏳ Add E2E tests (Playwright/Cypress)

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Vitest Documentation](https://vitest.dev/)
- [Testing Library](https://testing-library.com/react)
- [React Query Testing](https://tanstack.com/query/latest/docs/react/guides/testing)