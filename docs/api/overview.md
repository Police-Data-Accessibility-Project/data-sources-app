# API Overview

The Data Sources App exposes two API versions, both served from the same application.

| | v2 | v3 |
|---|---|---|
| **Framework** | Flask + Flask-RestX | FastAPI |
| **Base path** | `/api/v2` | `/api/v3` |
| **Auto-docs** | Swagger UI at `/api/v2/` | OpenAPI at `/api/v3/docs` |
| **Schema layer** | Marshmallow schemas (being migrated to Pydantic-generated) | Pydantic models only |
| **Auth** | Decorators | FastAPI dependency injection |
| **Status** | Stable, full-featured (29 namespaces) | Growing (3 routers) |

## Live Deployments

| Environment | URL | Branch |
|-------------|-----|--------|
| **Production** | https://data-sources.pdap.io/api | `main` |
| **Development** | https://data-sources.pdap.dev/api | `dev` |

Both environments serve v2 and v3 from the same deployment.

## v2 API (Flask-RestX)

The v2 API is the primary, full-featured API. It's built with Flask-RestX, which provides automatic Swagger documentation.

Endpoints are organized as Flask-RestX **namespaces**, each registered in `app.py`. A namespace is a logical grouping of related routes (e.g., `/agencies`, `/data-sources`, `/auth`).

### Namespace Structure

Each namespace lives in `endpoints/instantiations/{name}/`:

```
endpoints/instantiations/agencies_/
├── routes.py           # Namespace definition + Resource classes
├── get/
│   ├── by_id/          # GET /agencies/{id}
│   │   ├── core/
│   │   │   ├── query.py
│   │   │   └── schemas/
│   │   └── wrapper.py
│   └── many/           # GET /agencies
├── post/               # POST /agencies
├── put/                # PUT /agencies/{id}
└── delete/             # DELETE /agencies/{id}
```

This domain-prioritized organization keeps related files (query, schema, wrapper) close together. See [`DESIGN.md`](../../DESIGN.md) for the rationale behind this structure.

### Request/Response Patterns

v2 endpoints typically follow this pattern:

1. A Flask-RestX `Resource` class defines HTTP methods.
2. Each method is decorated with auth info (e.g., `@handle_auth(API_OR_JWT_AUTH_INFO)`).
3. The method calls a wrapper function in `middleware/primary_resource_logic/` or a local `wrapper.py`.
4. The wrapper interacts with the `DatabaseClient` or a `QueryBuilder`.
5. Results are returned as Pydantic DTO instances, converted via `dto_to_response()`.

### Schema Configuration

Endpoint schemas (for Swagger documentation) are configured in `endpoints/schema_config/`. These are being migrated to auto-generation from Pydantic DTOs via the `pydantic_to_marshmallow` conversion.

## v3 API (FastAPI)

The v3 API is built with FastAPI and is where new endpoints are developed. It currently includes three routers:

| Router | Path | Purpose |
|--------|------|---------|
| `sm_router` | `/api/v3/source_manager` | Source management operations |
| `user_router` | `/api/v3/user` | User-related endpoints |
| `permission_router` | `/api/v3/permissions` | Permission management |

v3 endpoints use Pydantic models directly for request validation and response serialization, and FastAPI's dependency injection for authentication.

## Common Conventions

### Rate Limiting

Rate limiting is applied globally via `flask-limiter`:
- **Default:** 100 requests per hour per IP.
- Individual endpoints can override with custom limits.
- Storage is in-memory (resets on app restart).

### CORS

CORS is configured at the Starlette level (wrapping both APIs) with allowed origins:
- `https://pdap.io`, `https://www.pdap.io`
- `https://data-sources.pdap.dev`, `https://pdap.dev`
- `https://data-sources.pdap.io`
- `http://localhost:8888` (local development)

### Output Formats

Most endpoints return JSON. Some support CSV output via the `OutputFormatEnum` (`json` or `csv`).

### Pagination

Endpoints that return lists support a `limit` parameter. Typeahead endpoints support pagination.

## Migration Plan (v2 to v3)

The long-term plan is to migrate fully to FastAPI. The coexistence approach allows:

- **New endpoints** to be built in v3 from the start.
- **Existing endpoints** to be migrated incrementally as needed.
- **Consumers** to adopt v3 endpoints at their own pace.

Both versions share the same database layer (`DatabaseClient`, `QueryBuilder`), security middleware, and business logic — only the HTTP layer differs.
