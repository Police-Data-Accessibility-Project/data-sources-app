# Endpoints

This is a summary of all registered API endpoint namespaces. For full request/response details, consult the auto-generated docs:

- **v2 Swagger UI:** https://data-sources.pdap.io/api
- **v3 OpenAPI docs:** https://data-sources.pdap.io/api/v3/docs

## v2 Endpoints (Flask-RestX)

All v2 endpoints are served under `/api/v2` (or just `/api` in older references). Each namespace is a Flask-RestX namespace registered in `app.py`.

### Core Resources

| Namespace | Path | Description |
|-----------|------|-------------|
| `data_source` | `/data-sources` | CRUD for data sources — the central resource. Supports search, filtering, and related entities. |
| `agencies` | `/agencies` | CRUD for law enforcement agencies. Agencies can have multiple locations and linked data sources. |
| `data_requests` | `/data-requests` | CRUD for data requests — community requests for specific data. Can be linked to data sources. |
| `locations` | `/locations` | Location data (states, counties, localities). |

### Search and Discovery

| Namespace | Path | Description |
|-----------|------|-------------|
| `search` | `/search` | Full-text search across data sources, supporting location and record type filters. |
| `typeahead_suggestions` | `/typeahead` | Autocomplete suggestions for locations and agencies. Backed by materialized views. |
| `match` | `/match` | Entity matching (e.g., match an agency by name). |
| `map` | `/map` | Map-related endpoints providing geographic data for states, counties, and localities. |
| `metadata` | `/metadata` | Reference data such as record types and categories. |
| `metrics` | `/metrics` | Analytics and usage metrics. |

### Authentication and Users

| Namespace | Path | Description |
|-----------|------|-------------|
| `auth` | `/auth` | Deprecated auth entry point. |
| `login` | `/auth/login` | Email/password login, returns JWT tokens. |
| `signup` | `/auth/signup` | New user registration. |
| `refresh_session` | `/auth/refresh-session` | Refresh an expired access token. |
| `request_reset_password` | `/auth/request-reset-password` | Request a password reset email. |
| `reset_password` | `/auth/reset-password` | Reset password with a token. |
| `reset_token_validation` | `/auth/reset-token-validation` | Check if a reset token is valid. |
| `validate_email` | `/auth/validate-email` | Validate a user's email address. |
| `resend_validation_email` | `/auth/resend-validation-email` | Resend the email validation link. |
| `callback` | `/auth/callback` | OAuth callback handler. |
| `user` | `/user` | User profile operations. |
| `admin` | `/admin` | Admin-only user management. |

### OAuth

| Namespace | Path | Description |
|-----------|------|-------------|
| `oauth` | `/oauth` | OAuth entry point. |
| `login_with_github` | `/oauth/login-with-github` | Initiate GitHub login flow. |
| `link_to_github` | `/oauth/link-to-github` | Link an existing account to GitHub. |

### Integrations and Utilities

| Namespace | Path | Description |
|-----------|------|-------------|
| `github` | `/github` | GitHub issue integration (create/read issues for data requests). |
| `notifications` | `/notifications` | User notification management. |
| `contact` | `/contact` | Contact form submission. |
| `url_checker` | `/check` | URL validation utility. |
| `source_collector` | `/source-collector` | Source collector tool endpoints. |
| `create_test_user` | `/dev` | Development-only: create test users with elevated permissions. |

## v3 Endpoints (FastAPI)

All v3 endpoints are served under `/api/v3`.

| Router | Path | Description |
|--------|------|-------------|
| `sm_router` | `/source_manager` | Source management — sync operations and source management workflows. |
| `user_router` | `/user` | User-related endpoints. |
| `permission_router` | `/permissions` | Permission management for users. |

## Adding a New Endpoint

### v2 (Flask-RestX)

1. Create a new directory under `endpoints/instantiations/{name}/`.
2. Define a namespace and Resource class in `routes.py`.
3. Add subdirectories for each HTTP method (`get/`, `post/`, etc.) with `core/` (query, schemas) and `wrapper.py`.
4. Register the namespace import in `app.py` and add it to the `NAMESPACES` list.

### v3 (FastAPI)

1. Create a new directory under `endpoints/v3/{name}/`.
2. Define a FastAPI `APIRouter` in `routes.py`.
3. Use Pydantic models for request/response validation.
4. Register the router in `create_fast_api_app()` in `app.py`.

For new endpoints, **prefer v3 (FastAPI)** unless you have a specific reason to use v2.
