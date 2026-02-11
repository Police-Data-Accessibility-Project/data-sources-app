# Contributing

Thanks for your interest in contributing to the PDAP Data Sources App! This guide will help you get started.

## Getting Started

1. **Set up the project** — Follow the [Development Setup](docs/development/setup.md) guide to install dependencies, configure environment variables, and set up a local database.
2. **Understand the architecture** — Read the [Architecture Overview](docs/architecture.md) and [DESIGN.md](DESIGN.md) for context on how the codebase is organized and why.

## Development Workflow

We use a two-branch model:

| Branch | Deploys to | Purpose |
|--------|------------|---------|
| `main` | [data-sources.pdap.io](https://data-sources.pdap.io) | Production |
| `dev` | [data-sources.pdap.dev](https://data-sources.pdap.dev) | Development / staging |

### Making Changes

1. Create a feature branch from `dev`.
2. Make your changes and add tests for new functionality.
3. Run checks locally before pushing (see below).
4. Open a PR targeting `dev`.
5. CI checks run automatically; a code owner will review your PR.
6. After merge to `dev`, changes deploy to the dev environment.
7. Periodically, `dev` is merged into `main` to deploy to production.

For full details on the PR process, CI checks, and commit conventions, see the [Workflow](docs/development/workflow.md) guide.

## Pre-Push Checklist

Before opening a PR, make sure your changes pass locally:

```bash
# Run tests (requires a running database — see Development Setup)
uv run pytest tests

# Lint and format
ruff check .
ruff format --check .

# Type check
uv run basedpyright --level error
```

For more on running and writing tests, see the [Testing](docs/development/testing.md) guide.

## Design Principles

- **Project design decisions**: [DESIGN.md](DESIGN.md)
- **PDAP-wide design philosophy**: [PDAP Design Principles](https://github.com/Police-Data-Accessibility-Project/meta/blob/main/DESIGN-PRINCIPLES.md)

## Questions?

If you're unsure how something works or where to start, reach out in [Discord](https://discord.gg/wMqex68Kkf) or email contact@pdap.io.

## Client App

See the [README at pdap.io](https://github.com/Police-Data-Accessibility-Project/pdap.io).
