# Documentation

This directory contains the documentation for the PDAP Data Sources App, the API powering [pdap.io](https://pdap.io).

## Contents

### Architecture
- **[Architecture Overview](architecture.md)** — How the system is structured: the dual Flask/FastAPI architecture, middleware layers, database layer, and request flow.

### API
- **[API Overview](api/overview.md)** — The v2 (Flask-RestX) and v3 (FastAPI) APIs, versioning strategy, and migration plan.
- **[Authentication](api/authentication.md)** — Auth methods (JWT, API key, OAuth), token lifecycle, and permission model.
- **[Endpoints](api/endpoints.md)** — Summary of available endpoint namespaces and what they do.

### Development
- **[Setup](development/setup.md)** — Getting the app running locally (environment, dependencies, database, secrets).
- **[Database](development/database.md)** — Schema overview, Alembic migrations, query builders, and test databases.
- **[Testing](development/testing.md)** — Running tests, writing tests, CI test infrastructure, and manual tests.
- **[Workflow](development/workflow.md)** — Branching strategy, PR process, CI/CD checks, and code standards.

### Reference
- **[Troubleshooting](troubleshooting.md)** — Common issues and how to fix them.

## Existing In-Repo Documentation

Several directories contain component-specific READMEs with additional detail:

| Location | Topic |
|----------|-------|
| [`DESIGN.md`](../DESIGN.md) | Architectural migration decisions (current and historical) |
| [`CHANGELOG.md`](../CHANGELOG.md) | Version history and breaking changes |
| [`ENV.md`](../ENV.md) | Full list of environment variables |
| [`CONTRIBUTING.md`](../CONTRIBUTING.md) | Contribution guidelines |
| [`endpoints/README.md`](../endpoints/README.md) | Flask-RestX swagger / namespace patterns |
| [`local_database/README.md`](../local_database/README.md) | Local test database setup |
| [`local_database/DataDumper/README.md`](../local_database/DataDumper/README.md) | Database backup/restore utility |
| [`relation_access_permissions/README.md`](../relation_access_permissions/README.md) | Column-level permission CSV config |
| [`middleware/` READMEs](../middleware/) | Various middleware component docs |
| [`db/queries/builder/mixins/README.md`](../db/queries/builder/mixins/README.md) | Query builder mixin docs |
