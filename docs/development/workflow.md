# Development Workflow

## Branching Strategy

The repository uses two long-lived branches:

| Branch | Purpose | Deployment |
|--------|---------|------------|
| `main` | Production | https://data-sources.pdap.io |
| `dev` | Development/staging | https://data-sources.pdap.dev |

### Workflow

1. Create a feature branch from `dev`.
2. Make changes, commit, push.
3. Open a PR into `dev`.
4. CI checks run automatically.
5. After review and merge to `dev`, changes deploy to the dev environment.
6. Periodically, `dev` is merged into `main` via a PR to deploy to production.

## Pull Requests

### Before Opening a PR

- Run linting: `ruff check . && ruff format --check .`
- Run tests: `uv run pytest tests`
- Ensure your changes include tests for new functionality.
- Run pre-commit hooks: `pre-commit run --all-files`

### PR Process

1. Open a PR targeting `dev` (or `main` for hotfixes).
2. CI checks run automatically (see below).
3. The `auto-populate-pr.yml` workflow extracts linked issue numbers from commit history for PRs into `main`.
4. Request review from a code owner (see `CODEOWNERS`).
5. Address review feedback.
6. Merge after approval and passing checks.

## CI/CD Checks

Five GitHub Actions run on every pull request:

| Workflow | File | What It Does | Blocking? |
|----------|------|-------------|-----------|
| **Pytest** | `run_pytest.yml` | Runs full test suite against a fresh PostgreSQL instance | Yes |
| **Ruff** | `ruff.yaml` | Linting and formatting checks | Yes |
| **Pyright** | `python_checks.yml` | Type checking with basedpyright (posts advisory comments) | No (advisory) |
| **Bandit** | `bandit.yaml` | Security vulnerability scanning | Yes |
| **PR Auto-Populate** | `auto-populate-pr.yml` | Extracts issue numbers from commits (main PRs only) | No |

### Fixing CI Failures

**Ruff (linting/formatting):**
```bash
ruff check --fix .    # Auto-fix lint issues
ruff format .         # Auto-format code
```

**Pytest:** Check the test output in the GitHub Actions log. Make sure your local `alembic upgrade head` succeeds against a fresh database.

**Basedpyright:** Add type hints to your modified code. These are advisory — they won't block your PR, but fixing them is encouraged.

**Bandit:** Address any security findings. Bandit scans `middleware/`, `resources/`, `app.py`, and `database_client/`.

## Code Standards

### Linting and Formatting

- **Tool:** [Ruff](https://docs.astral.sh/ruff/)
- **Config:** `pyproject.toml` (under `[tool.ruff]`)
- Enforced in CI on every PR.

```bash
ruff check .              # Lint
ruff check --fix .        # Lint and auto-fix
ruff format --check .     # Check formatting
ruff format .             # Format code
```

### Type Checking

- **Tool:** [basedpyright](https://github.com/DetachHead/basedpyright) (mypy-compatible)
- **Config:** `pyproject.toml` (under `[tool.basedpyright]`)
- Advisory in CI — posts comments on modified files missing type hints.

### Docstrings

- **Tool:** [pydocstyle](https://www.pydocstyle.org/en/stable/)
- **Config:** `.pydocstyle`
- Checks D100-D106 (module, class, method, function docstrings).
- Advisory in CI — will not block PRs.

### Security Scanning

- **Tool:** [Bandit](https://bandit.readthedocs.io/)
- Runs on every PR, scanning core application code.

## Versioning

The project uses [Commitizen](https://commitizen-tools.github.io/commitizen/) for semantic versioning and changelog generation. The current version is tracked in `pyproject.toml`.

### Commit Message Format

Follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
type(scope): description

# Examples:
feat(api): add /contact/form-submit endpoint
fix(db_client): fix bug in get_metrics()
refactor(resources): rename GET_AUTH_INFO to API_OR_JWT_AUTH_INFO
```

**Types:** `feat`, `fix`, `refactor`, `test`, `docs`, `ci`, `chore`

**Breaking changes:** Add `BREAKING CHANGE:` in the commit body or use `!` after the type:
```
feat(api)!: remove batch update endpoints
```

## Design Principles

For architectural decisions and migration patterns (e.g., directory organization, query builders, DTO patterns), see [`DESIGN.md`](../../DESIGN.md).

For broader PDAP design philosophy, see the [PDAP Design Principles](https://github.com/Police-Data-Accessibility-Project/meta/blob/main/DESIGN-PRINCIPLES.md).
