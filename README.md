![Python Version](https://img.shields.io/badge/python-3.12-blue?style=for-the-badge&logo=python&logoColor=ffdd54)

# data-sources-app

An API for searching, using, and maintaining Data Sources, built by the [Police Data Accessibility Project (PDAP)](https://pdap.io).

#### Live app: https://data-sources.pdap.io/ deployed from `main`
#### Dev app: https://data-sources.pdap.dev/ deployed from `dev`
#### API docs / base URL: https://data-sources.pdap.io/api (or ...dev/api)

## Documentation

Full documentation is in the [`docs/`](docs/) directory:

- **[Architecture Overview](docs/architecture.md)** — System design, dual Flask/FastAPI architecture, directory structure.
- **[API Overview](docs/api/overview.md)** — v2 and v3 APIs, versioning, and migration plan.
- **[Authentication](docs/api/authentication.md)** — JWT, API keys, OAuth, and permissions.
- **[Endpoints](docs/api/endpoints.md)** — All available endpoints and what they do.
- **[Development Setup](docs/development/setup.md)** — Full setup guide (dependencies, database, secrets).
- **[Database](docs/development/database.md)** — Schema, migrations, query builders.
- **[Testing](docs/development/testing.md)** — Running and writing tests.
- **[Workflow](docs/development/workflow.md)** — Branching, PRs, CI/CD, code standards.
- **[Troubleshooting](docs/troubleshooting.md)** — Common issues and fixes.

## Quick Start

```bash
# Clone
git clone https://github.com/Police-Data-Accessibility-Project/data-sources-app.git
cd data-sources-app

# Install dependencies (using uv)
pip install uv
uv sync --locked --all-extras --dev

# Set up pre-commit hooks
pre-commit install

# Configure environment (see docs/development/setup.md and ENV.md)
cp .env.example .env  # Then edit with your values

# Set up local database
cd local_database && python setup.py && cd ..
uv run alembic upgrade head

# Run the app
python app.py
```

For the full setup guide with all options, see [Development Setup](docs/development/setup.md).

## Contributing

Please review [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a Pull Request. For architecture and design decisions, see [DESIGN.md](DESIGN.md).
