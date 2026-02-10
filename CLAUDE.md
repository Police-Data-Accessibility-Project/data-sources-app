# CLAUDE.md - Project Guide for Claude Code

## Project Overview

This is the **PDAP Data Sources API** — the backend for the [Police Data Accessibility Project](https://pdap.io), a civic-tech initiative that catalogs police data sources across the United States. It provides endpoints for searching data sources, managing agencies, handling data requests, user authentication, notifications, and admin operations.

- **Production**: https://data-sources.pdap.io/ (deployed from `main`)
- **Development**: https://data-sources.pdap.dev/ (deployed from `dev`)
- **API docs**: https://data-sources.pdap.io/api

## Tech Stack

- **Python 3.12** (specified in `runtime.txt` and `Dockerfile`)
- **Dual API framework**: Flask-RESTX (v2 at `/api/v2`) + FastAPI (v3 at `/api/v3`), unified under Starlette ASGI
- **Database**: PostgreSQL 15 via SQLAlchemy ORM + psycopg 3 driver
- **Migrations**: Alembic
- **Auth**: Flask-JWT-Extended + Authlib (GitHub OAuth)
- **Validation**: Pydantic 2 DTOs auto-converted to Marshmallow schemas via `pydantic_to_marshmallow`
- **Package manager**: uv (with `uv.lock`)
- **Server**: Gunicorn + UvicornWorker (production), Uvicorn (development)

## Common Commands

```bash
# Install dependencies
uv sync --locked --all-extras --dev

# Run the app locally
python app.py

# Run all tests
uv run pytest tests

# Run a specific test file or directory
uv run pytest tests/integration/agencies/

# Run database migrations
uv run alembic upgrade head

# Create a new migration
uv run alembic revision --autogenerate -m "description"

# Lint
uv run ruff check .

# Type check
uv run basedpyright --level error
```

## Local Database Setup

Spin up a local PostgreSQL 15 via Docker:
```bash
cd local_database
docker compose -f docker_compose.yml up -d
```
Then set `DO_DATABASE_URL=postgresql://test_data_sources_app_user:ClandestineCornucopiaCommittee@localhost:5432/test_data_sources_app_db` and run `alembic upgrade head`.

## Required Environment Variables

Set in a `.env` file at project root. See `ENV.md` for full details. Key variables:
- `DO_DATABASE_URL` — PostgreSQL connection string
- `JWT_SECRET_KEY`, `RESET_PASSWORD_SECRET_KEY`, `VALIDATE_EMAIL_SECRET_KEY` — JWT signing keys
- `FLASK_APP_COOKIE_ENCRYPTION_KEY` — Flask secret key
- `GH_CLIENT_ID`, `GH_CLIENT_SECRET`, `GH_API_ACCESS_TOKEN`, `GH_CALLBACK_URL` — GitHub OAuth/API
- `DEVELOPMENT_PASSWORD` — Test user creation
- `WEBHOOK_URL`, `TEST_EMAIL_ADDRESS`, `FLAG_RUN_SCHEDULED_JOBS`

## Project Structure

```
app.py                  # Application entry point — creates Flask, FastAPI, and Starlette ASGI apps
config.py               # Global config (OAuth, rate limiter, JWT manager)
execute.sh              # Production entrypoint (gunicorn + uvicorn)

db/                     # Database layer
  client/               # DatabaseClient class (core.py) with context managers and decorators
  models/               # SQLAlchemy ORM models (core tables, link tables, materialized views)
  queries/              # Query Builder pattern (QueryBuilderBase ABC + domain instantiations)
  dtos/                 # Database-level DTOs
  enums.py              # DB enums (LocationType, RequestStatus, etc.)

endpoints/              # API endpoint layer
  instantiations/       # Flask-RESTX v2 endpoints (one directory per namespace)
  v3/                   # FastAPI v3 endpoints (permissions, source_manager, user)
  schema_config/        # SchemaConfigs enum mapping endpoints to input/output schemas
  psycopg_resource.py   # PsycopgResource base class for Flask-RESTX resources

middleware/             # Business logic layer
  primary_resource_logic/   # Business logic per domain
  security/                 # Auth system (JWT, API keys, access info)
  schema_and_dto/           # Schema/DTO infrastructure + pydantic_to_marshmallow
  decorators/               # endpoint_info, authentication_required, api_key_required
  dynamic_request_logic/    # Dynamic GET/POST/PUT/DELETE handlers
  scheduled_tasks/          # APScheduler tasks (health checks, materialized view refresh)

tests/                  # Primary test suite (pytest)
  conftest.py           # Fixtures (DB setup, clients, test data creators)
  integration/          # Integration tests organized by domain
  db_client/            # Database client unit tests
  middleware/           # Middleware unit tests

tests_comprehensive/    # Cross-cutting tests (bad requests, forbidden, unauthorized)
alembic/                # Database migration files
utilities/              # Shared utilities
local_database/         # Local dev database (Docker Compose + data dump/restore)
```

## Architecture & Design Patterns

Refer to `DESIGN.md` for detailed rationale. Key patterns:

### Domain-Driven Directory Organization (Active Migration)
Files are being migrated from type-based organization (`middleware/schema_and_dto/`, `middleware/primary_resource_logic/`) to domain-based organization under `endpoints/instantiations/{namespace}/{route}/`. Shared files go in the closest common parent directory.

### Query Builder Pattern
Complex queries use classes extending `QueryBuilderBase` (ABC with `run()` method), executed via `DatabaseClient.run_query_builder()`. Located in `db/queries/`.

### Pydantic-to-Marshmallow Conversion
Pydantic DTOs are auto-converted to Marshmallow schemas for Flask-RESTX Swagger documentation. New endpoints should define Pydantic DTOs only and use `pydantic_to_marshmallow` for schema generation.

### CTE Wrapper Classes
SQLAlchemy CTEs are wrapped in classes with type-hinted properties instead of using raw `.c.column_name` access.

### Endpoint Info Decorator
The `@endpoint_info` meta-decorator on v2 endpoints combines authentication, exception handling, and Swagger documentation.

### PsycopgResource
All Flask-RESTX resources inherit from `PsycopgResource`, which provides `run_endpoint()` for standardized request handling with DB client context management.

## Testing

- Tests use **pytest** and require a running PostgreSQL instance
- CI runs against a PostgreSQL 15 Docker service with Alembic migrations applied
- Key fixtures in `tests/conftest.py`:
  - `setup_database` (session-scoped, autouse): runs migrations, drops on teardown
  - `live_database_client`: provides `DatabaseClient` with wiped DB
  - `flask_client`: Flask test client with mocked scheduler + disabled rate limiter
  - `test_data_creator_flask` / `test_data_creator_db_client`: factories for test data
  - `bypass_jwt_required`: monkeypatches JWT verification
- Integration tests mirror endpoint structure under `tests/integration/`

## CI/CD (GitHub Actions)

All triggered on pull requests:
1. **run_pytest.yml** — PostgreSQL 15 service, `alembic upgrade head`, `pytest tests` (20-min timeout)
2. **ruff.yaml** — Ruff lint check
3. **bandit.yaml** — Security linting
4. **python_checks.yml** — basedpyright type checking at error level
5. **auto-populate-pr.yml** — Extracts issue numbers from PR commits

## Code Conventions

- **Files/functions**: `snake_case`
- **Classes**: `PascalCase`
- **Enums**: `PascalCase` class, `UPPER_SNAKE_CASE` members
- **Imports**: Absolute imports only (e.g., `from db.client.core import DatabaseClient`)
- **Endpoint directories**: Some use trailing underscores (e.g., `agencies_/`) to avoid name conflicts
- **Responses**: Return Pydantic DTO objects processed via `dto_to_response`; tests validate output against schemas
- **Ruff rules**: Ignores F821, F403, E721 (see `pyproject.toml`)
- **Type checking**: basedpyright with many rules temporarily disabled (see `pyproject.toml`)
- **Commit style**: Conventional Commits (via Commitizen)

## Branching Strategy

- `main` = production
- `dev` = development/staging
- Feature branches → PRs with CI checks → merge
