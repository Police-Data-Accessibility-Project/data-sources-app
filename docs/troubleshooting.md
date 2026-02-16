# Troubleshooting

Common issues and their solutions.

## Setup Issues

### `ModuleNotFoundError` when running the app

**Cause:** Dependencies not installed, or the virtual environment is not activated.

**Fix:**
```bash
# If using uv:
uv sync --locked --all-extras --dev

# If using pip + virtualenv:
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment variable errors on startup

**Cause:** Missing required `.env` file or environment variables.

**Fix:** Ensure all required variables from [`ENV.md`](../ENV.md) are set. At minimum you need `DO_DATABASE_URL`, `JWT_SECRET_KEY`, `FLASK_APP_COOKIE_ENCRYPTION_KEY`, `GH_CLIENT_ID`, and `GH_CLIENT_SECRET`. See [Setup](development/setup.md#4-configure-environment-variables) for a minimal `.env` example.

### `psycopg` connection errors

**Cause:** Incorrect `DO_DATABASE_URL` format or the database is unreachable.

**Fix:**
- Verify your connection string format: `postgresql+psycopg://user:password@host:port/dbname`
- For the local Docker database: ensure Docker is running and the container is up (`docker compose -f local_database/docker_compose.yml up -d`).
- For the sandbox database: ensure you're connected to the internet and the credentials are current (sandbox is refreshed daily).

## Database Issues

### Alembic migration fails

**Cause:** Migration conflicts, missing dependencies, or a database in an unexpected state.

**Fix:**
```bash
# Check current migration state
uv run alembic current

# If the database is ahead of your migrations (e.g., after pulling new code)
uv run alembic upgrade head

# If the database is in a broken state (local Docker only!), reset:
docker compose -f local_database/docker_compose.yml down
docker compose -f local_database/docker_compose.yml up -d
uv run alembic upgrade head
```

### `relation "X" does not exist` errors in tests

**Cause:** Migrations haven't been run against the test database.

**Fix:**
```bash
uv run alembic upgrade head
```

CI always runs migrations before tests. Locally, you need to do this manually after pulling new migration files.

### Empty local database

**Cause:** The local Docker database starts with no data — it only has the schema from migrations.

**Fix:** Either:
- Use the [DataDumper](../local_database/DataDumper/README.md) to populate it from a backup.
- Or point `DO_DATABASE_URL` at the sandbox database instead.

## Test Issues

### Tests fail locally but pass in CI (or vice versa)

**Common causes:**
- Different database state (CI starts fresh every time; local may have stale data).
- Different Python version (CI uses 3.12.8 specifically).
- Missing environment variables (CI uses specific dummy values — see `run_pytest.yml`).

**Fix:** Ensure your local environment matches CI:
```bash
# Check Python version
python --version  # Should be 3.12.x

# Reset local DB
docker compose -f local_database/docker_compose.yml down
docker compose -f local_database/docker_compose.yml up -d
uv run alembic upgrade head
```

### Tests timeout or hang

**Cause:** Usually a database connection issue or a test waiting for a response from an unreachable service.

**Fix:**
- Ensure your database is reachable.
- Check if any tests depend on external services (these should be in `manual_tests/`, not `tests/`).

## CI Issues

### Ruff check fails

**Fix:**
```bash
ruff check --fix .
ruff format .
```

Then commit the changes.

### Bandit flags a false positive

If Bandit flags code that you believe is safe, you can add an inline `# nosec` comment with a justification. Use this sparingly.

### Basedpyright posts type checking comments

These are **advisory only** and do not block the PR. To resolve them, add type hints to the flagged code. This is encouraged but not required.

## Runtime Issues

### Rate limiting (429 Too Many Requests)

**Cause:** The default rate limit is 100 requests per hour per IP.

**Fix:** Wait for the rate limit to reset, or (for development) note that rate limiting is in-memory and resets on app restart.

### CORS errors from the client

**Cause:** The requesting origin is not in the CORS allow list.

**Fix:** For local development, ensure the client is running on `http://localhost:8888` (the allowed dev origin). If you need a different port, the CORS config is in `app.py` in the `create_asgi_app()` function.

### Scheduled jobs not running

**Cause:** The `FLAG_RUN_SCHEDULED_JOBS` environment variable is not set or is `False`.

**Fix:** Set `FLAG_RUN_SCHEDULED_JOBS=True` in your `.env` to enable materialized view refreshes and health checks. Note: you generally don't need these for local development.

## Getting Help

- **Discord:** Reach out to @maxachis or @joshuagraber.
- **Email:** contact@pdap.io
- **Issues:** https://github.com/Police-Data-Accessibility-Project/data-sources-app/issues
