# Architecture Overview

The Data Sources App is a Python REST API for searching, using, and maintaining police data sources on behalf of the [Police Data Accessibility Project (PDAP)](https://pdap.io).

## High-Level Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.12 |
| ASGI server | Gunicorn + Uvicorn workers |
| API framework (v2) | Flask + Flask-RestX |
| API framework (v3) | FastAPI |
| ASGI glue | Starlette (mounts both apps) |
| Database | PostgreSQL (hosted on DigitalOcean) |
| ORM / query | SQLAlchemy (models + query builders) |
| Migrations | Alembic |
| Auth | JWT (flask-jwt-extended), OAuth (GitHub via authlib), API keys |
| Rate limiting | flask-limiter (in-memory) |
| Scheduled jobs | APScheduler |
| Package management | uv (with lockfile) |
| Deployment | Docker container on DigitalOcean App Platform |

## Dual API Architecture

The app serves **two API versions** from a single Starlette ASGI application:

```
Starlette (root ASGI app)
├── /api/v2  →  Flask app (via WSGIMiddleware)
│                └── Flask-RestX namespaces (29 endpoints)
└── /api/v3  →  FastAPI app
                 └── FastAPI routers (3 routers)
```

This is configured in `app.py`:

- `create_flask_app()` builds the Flask app with all v2 namespaces, JWT, OAuth, rate limiting, and scheduled jobs.
- `create_fast_api_app()` builds the FastAPI app with v3 routers.
- `create_asgi_app()` creates the Starlette root, adds CORS middleware, and mounts both apps.

**Why two frameworks?** The app was originally Flask-only. FastAPI is being adopted incrementally for new endpoints due to its native async support, automatic OpenAPI docs from Pydantic models, and simpler patterns. See [`DESIGN.md`](../DESIGN.md) for the full migration rationale.

### Auto-Generated API Docs

- **v2 (Flask-RestX):** Swagger UI at the `/api/v2/` root (rendered by Flask-RestX automatically).
- **v3 (FastAPI):** OpenAPI docs at `/api/v3/docs` (rendered by FastAPI automatically).

## Request Flow

A typical authenticated v2 request goes through these layers:

```
Client request
  → Starlette CORS middleware
  → Flask app (via WSGIMiddleware)
    → Flask-Limiter (rate limiting)
    → Flask-RestX route dispatch
      → Authentication decorator (JWT / API key / OAuth check)
      → Endpoint resource class
        → Middleware (primary_resource_logic / dynamic_request_logic)
          → DatabaseClient / QueryBuilder
            → SQLAlchemy → PostgreSQL
          ← DTO response (Pydantic BaseModel)
        ← dto_to_response() → JSON
      ← Flask-RestX marshalling (optional)
    ← HTTP response
```

For v3, the flow is similar but uses FastAPI's dependency injection for auth, and Pydantic models directly for request/response validation.

## Directory Structure

```
├── app.py                          # ASGI app creation (Flask + FastAPI + Starlette)
├── config.py                       # Global config (OAuth, limiter, JWT, DB connection)
├── alembic/                        # Database migrations
│   ├── env.py
│   └── versions/                   # Migration scripts (YYYY_MM_DD_HHMM-{rev}_{slug}.py)
├── db/                             # Database layer
│   ├── client/                     # DatabaseClient (central DB abstraction)
│   ├── models/                     # SQLAlchemy ORM models
│   ├── queries/                    # Query builders (QueryBuilderBase subclasses)
│   │   ├── builder/                # Base classes and mixins
│   │   └── ctes/                   # CTE/Subquery wrapper classes
│   ├── dtos/                       # Data Transfer Objects (Pydantic BaseModels)
│   ├── helpers_/                   # DB utility functions
│   ├── enums.py                    # Database-level enumerations
│   └── constants.py
├── endpoints/                      # API endpoint definitions
│   ├── instantiations/             # v2 Flask-RestX endpoints (one dir per namespace)
│   │   └── {namespace}/
│   │       ├── routes.py           # Namespace definition + Resource classes
│   │       ├── get/, post/, put/, delete/
│   │       │   ├── core/           # query.py, schemas/
│   │       │   └── wrapper.py
│   │       └── shared/             # Shared logic within the namespace
│   ├── v3/                         # v3 FastAPI endpoints
│   │   ├── source_manager/         # /api/v3/source_manager
│   │   ├── user/                   # /api/v3/user
│   │   └── permissions/            # /api/v3/permissions
│   ├── schema_config/              # Endpoint schema configurations
│   └── _helpers/                   # Shared endpoint utilities
├── middleware/                      # Business logic and cross-cutting concerns
│   ├── security/                   # Auth, JWT, API keys, access control
│   │   ├── auth/                   # Authentication methods and config
│   │   ├── jwt/                    # JWT token management
│   │   ├── api_key/                # API key validation
│   │   └── access_info/            # Access info DTOs
│   ├── primary_resource_logic/     # Resource-specific business logic
│   ├── dynamic_request_logic/      # Reusable parameter-driven middleware
│   ├── schema_and_dto/             # Schema/DTO management and conversion
│   ├── third_party_interaction_logic/  # GitHub, Mailgun integrations
│   ├── scheduled_tasks/            # APScheduler jobs
│   ├── decorators/                 # Custom decorators (@endpoint_info, etc.)
│   ├── util/                       # Utility functions
│   └── enums.py                    # Middleware-level enumerations
├── relation_access_permissions/    # Role-based column permission CSVs
├── utilities/                      # Global utility modules
├── tests/                          # Pytest test suite
├── local_database/                 # Docker-based local test DB setup
├── manual_tests/                   # Scripts for testing third-party integrations
└── .github/                        # CI/CD workflows
```

## Key Components

### DatabaseClient (`db/client/core.py`)

The central abstraction for all database operations. It manages the psycopg connection and delegates complex queries to QueryBuilder classes via `run_query_builder()`.

### QueryBuilderBase (`db/queries/builder/core.py`)

Base class for type-safe, composable query construction. Subclasses implement `run()` which receives a SQLAlchemy session. Query builders are the preferred pattern for anything beyond simple queries — see [`DESIGN.md`](../DESIGN.md).

### CTE/Subquery Wrappers (`db/queries/ctes/`)

Type-safe wrapper classes around SQLAlchemy CTEs and subqueries. Columns are exposed as typed properties instead of raw `.c.column_name` access, improving discoverability and catching typos at the type-checking level.

### Security / Auth (`middleware/security/`)

Authentication is configured per-endpoint via `AuthenticationInfo` objects that specify:
- **Allowed access methods:** JWT, API key, reset password token, email validation token, or no auth.
- **Required permissions:** e.g., `DB_WRITE`, `NOTIFICATIONS`, `SOURCE_COLLECTOR`.
- **Auth scheme:** Bearer (JWT) or Basic (API key).

See [Authentication](api/authentication.md) for details.

### Scheduled Tasks (`middleware/scheduled_tasks/`)

APScheduler runs periodic jobs when `FLAG_RUN_SCHEDULED_JOBS=True`:
- Database health checks (every 60 minutes)
- Materialized view refreshes for typeahead and map data

### Relation Access Permissions (`relation_access_permissions/`)

CSV-based column-level permission configuration. Each CSV represents a database table, with columns defining read/write/none access per role (e.g., STANDARD, ADMIN). These are uploaded to the database during the automated prod-to-dev migration job.
