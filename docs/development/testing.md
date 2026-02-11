# Testing

## Test Suite Overview

Tests live in the `tests/` directory and are run with [pytest](https://docs.pytest.org/en/stable/).

```
tests/
├── conftest.py                 # Shared fixtures (DB clients, mock clients, etc.)
├── fixtures.py                 # Additional fixtures
├── test_database.py            # Database integration tests
├── test_pydantic_to_marshmallow.py  # Schema conversion tests
├── test_schema_validation.py   # Schema validation tests
├── test_schema_aligned_with_db_table.py  # Schema-DB alignment tests
├── db_client/                  # DatabaseClient unit tests
├── integration/                # Integration tests
│   └── notifications/          # Notification event flow tests
├── middleware/                  # Middleware logic tests
├── helpers/                    # Test helper functions
├── utilities/                  # Utility tests
├── _mocks/                     # Mock data and fixtures
└── alembic/                    # Migration tests
```

## Running Tests

### Prerequisites

You need a database connection. Either:
- A running local Docker database (see [Database Setup](database.md)), or
- A sandbox database connection string.

Set `DO_DATABASE_URL` in your `.env` file.

### Run All Tests

```bash
uv run pytest tests
```

### Run Specific Tests

```bash
# Run a single file
uv run pytest tests/test_database.py

# Run a specific test function
uv run pytest tests/test_database.py::test_function_name

# Run tests in a directory
uv run pytest tests/middleware/

# Run with verbose output
uv run pytest tests -v
```

### CI Test Execution

Tests run automatically on every pull request via the `run_pytest.yml` GitHub Action:

1. A fresh PostgreSQL 15 container is started.
2. Dependencies are installed with `uv sync --locked --all-extras --dev`.
3. Alembic migrations are run against the fresh database.
4. `uv run pytest tests` runs all tests.
5. Tests have a 20-minute timeout.

The CI environment uses dummy values for auth secrets (JWT keys, GitHub OAuth) — these are sufficient for tests that don't make real external calls.

## Writing Tests

### Conventions

- Place tests in the appropriate subdirectory matching the code being tested.
- Use fixtures from `conftest.py` for database clients and mock setup.
- Test output schemas to validate response format.
- Use Pydantic DTOs to validate response structure where applicable.

### Key Fixtures (from `conftest.py`)

The test suite provides fixtures for database access and mock setup. Check `tests/conftest.py` and `tests/fixtures.py` for the current list.

### Testing Query Builders

Query builders can be tested by running them against the test database:

```python
def test_my_query(dev_db_client):
    result = dev_db_client.run_query_builder(MyQuery(...))
    assert result is not None
```

### Testing Endpoints

Endpoint tests typically use Flask's test client or FastAPI's TestClient to make requests and validate responses against expected schemas.

## Manual Tests

Manual tests for third-party integrations (GitHub, email/Mailgun) live in `manual_tests/`. These require real credentials and are not run in CI.

See [`manual_tests/README.md`](../../manual_tests/README.md) for instructions.

## Test Databases

Two remote test databases are available:

| Database | Purpose | Sensitive Data? |
|----------|---------|-----------------|
| **Sandbox** | Developer testing, schema experiments | No |
| **Stage** | Pre-release integration testing | Yes |

Both are refreshed daily from production. Connection details are available through DigitalOcean (admin access required) or environment variables on the Jenkins migration job. Reach out to the team in [Discord](https://discord.gg/wMqex68Kkf) for access.
