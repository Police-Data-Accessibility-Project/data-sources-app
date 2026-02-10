# Development Setup

This guide consolidates all the steps needed to get the Data Sources App running locally.

## Prerequisites

- **Python 3.12** (specifically 3.12.8 for CI parity)
- **Docker** — for the local test database ([install](https://docs.docker.com/engine/install/))
- **Git**

## 1. Clone and Navigate

```bash
git clone https://github.com/Police-Data-Accessibility-Project/data-sources-app.git
cd data-sources-app
```

## 2. Install Dependencies

The project uses [uv](https://docs.astral.sh/uv/) for package management (matching CI and Docker builds):

```bash
# Install uv if you don't have it
pip install uv

# Install all dependencies from the lockfile
uv sync --locked --all-extras --dev
```

**Alternative (pip):** If you prefer pip, you can use virtualenv:

```bash
pip install virtualenv
virtualenv -p python3.12 venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install "psycopg[binary,pool]"
```

## 3. Set Up Pre-Commit Hooks

```bash
pre-commit install

# Optionally run against all files
pre-commit run --all-files
```

## 4. Configure Environment Variables

Create a `.env` file in the project root. See [`ENV.md`](../../ENV.md) for the full list.

**Minimum required for local development:**

```dotenv
# Database connection (see step 5 for local DB, or use sandbox)
DO_DATABASE_URL="postgresql+psycopg://test_data_sources_app_user:ClandestineCornucopiaCommittee@127.0.0.1:5432/test_data_sources_app_db"

# Auth (can be dummy values for local development)
JWT_SECRET_KEY="myLocalJwtSecretKey"
FLASK_APP_COOKIE_ENCRYPTION_KEY="myLocalCookieKey"
RESET_PASSWORD_SECRET_KEY="myLocalResetKey"
VALIDATE_EMAIL_SECRET_KEY="myLocalValidateKey"

# GitHub OAuth (get real values from the team, or use dummies if not testing OAuth)
GH_CLIENT_ID="GithubProvidedClientId"
GH_CLIENT_SECRET="GithubProvidedClientSecret"
GH_CALLBACK_URL="http://localhost:8000/api/v2/auth/callback"
```

For full access to all secrets, reach out to contact@pdap.io or ask in Discord.

## 5. Set Up the Database

You have two options:

### Option A: Local Docker Database (Recommended for Schema Work)

This creates an empty local PostgreSQL instance, useful for testing migrations and schema changes.

```bash
# From the repository root
cd local_database
python setup.py
```

Or manually:

```bash
cd local_database
docker compose -f docker_compose.yml up -d
```

Then set your `.env`:

```dotenv
DO_DATABASE_URL="postgresql+psycopg://test_data_sources_app_user:ClandestineCornucopiaCommittee@127.0.0.1:5432/test_data_sources_app_db"
```

Run migrations to create the schema:

```bash
uv run alembic upgrade head
```

To populate with data, see the [DataDumper](../../local_database/DataDumper/README.md) instructions.

To stop the database:

```bash
docker compose -f docker_compose.yml down
```

### Option B: Sandbox Database (Recommended for Feature Development)

The sandbox is a remote database refreshed daily from production (with sensitive data excluded). Get connection credentials from the team — see [CONTRIBUTING.md](../../CONTRIBUTING.md) for details.

Set `DO_DATABASE_URL` in your `.env` to the sandbox connection string.

## 6. Run the App

### Development (local)

```bash
python app.py
```

This starts uvicorn on `127.0.0.1:8000` by default.

### Production-like (Docker)

```bash
# The execute.sh script runs gunicorn with uvicorn workers
docker build -t data-sources-app .
docker run -p 8080:8080 --env-file .env data-sources-app ./execute.sh
```

### Verifying It Works

- **v2 Swagger:** http://localhost:8000/api/v2/
- **v3 OpenAPI:** http://localhost:8000/api/v3/docs

## 7. Running the Client Locally (If Needed)

If you need to run the [pdap.io](https://github.com/Police-Data-Accessibility-Project/pdap.io) client against your local API:

1. Set `VITE_VUE_API_BASE_URL=http://localhost:8000` in the client's environment.
2. Reach out to @maxachis or @joshuagraber in Discord for help with full-stack local development.

Generally, local API development can be verified using `curl` or the Swagger UI without running the client.
