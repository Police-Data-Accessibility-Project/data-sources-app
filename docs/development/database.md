# Database

The app uses PostgreSQL, accessed via SQLAlchemy for ORM operations and psycopg for the connection layer. Database changes are managed with Alembic migrations.

## Environments

| Environment | Purpose | Sensitive Data? | Refreshed |
|-------------|---------|-----------------|-----------|
| **Production** | Live app (DigitalOcean) | Yes | N/A |
| **Sandbox** | Developer testing | No (excluded) | Daily from prod |
| **Stage** | Pre-release testing | Yes | Daily from prod |
| **Local Docker** | Schema/migration work | No (empty or dumped) | Manual |

Both sandbox and stage are refreshed daily via the [prod-to-dev-migration](https://github.com/Police-Data-Accessibility-Project/prod-to-dev-migration) repository.

## Key Tables

The database contains many tables. Here are the primary ones, grouped by domain. The full list of relations is in `middleware/enums.py` under the `Relations` enum.

### Core Data

| Table | Description |
|-------|-------------|
| `data_sources` | Police data sources — the central resource |
| `data_sources_expanded` | View with joined agency/location data |
| `agencies` | Law enforcement agencies |
| `agencies_expanded` | View with joined location data |
| `data_requests` | Community data requests |
| `data_requests_expanded` | View with expanded request data |

### Locations

| Table | Description |
|-------|-------------|
| `locations` | Canonical location records |
| `locations_expanded` | View with full location hierarchy |
| `us_states` | US states reference |
| `counties` | Counties reference |
| `localities` | Cities/towns reference |

### Users and Auth

| Table | Description |
|-------|-------------|
| `users` | User accounts |
| `pending_users` | Unverified user registrations |
| `external_accounts` | Linked OAuth accounts (GitHub) |
| `reset_tokens` | Password reset tokens |
| `permissions` | Permission definitions |
| `link_users__permissions` | User-permission assignments |

### Link Tables

| Table | Description |
|-------|-------------|
| `link_agencies__data_sources` | Agency ↔ Data source relationships |
| `link_agencies__locations` | Agency ↔ Location relationships |
| `link_data_requests__data_sources` | Data request ↔ Data source relationships |
| `link_data_requests__locations` | Data request ↔ Location relationships |
| `link_user_followed_location` | User location follows |

### Search and Caching

| Table | Description |
|-------|-------------|
| `recent_searches` | User search history |
| `record_types` | Record type definitions |
| `record_categories` | Record category groupings |

### Materialized Views

These are refreshed periodically by scheduled jobs:

| View | Description |
|------|-------------|
| `typeahead_locations` | Autocomplete data for location search |
| `typeahead_agencies` | Autocomplete data for agency search |
| `map_states` | State-level map data |
| `map_counties` | County-level map data |
| `map_localities` | Locality-level map data |

### Notifications

| Table | Description |
|-------|-------------|
| `data_request_pending_event_notification` | Pending notification events for data requests |
| `data_source_pending_event_notification` | Pending notification events for data sources |
| `data_request_user_notification_queue` | User notification queue for data requests |
| `data_source_user_notification_queue` | User notification queue for data sources |
| `notification_log` | Sent notification history |

### Auditing

| Table | Description |
|-------|-------------|
| `change_log` | Tracks UPDATE and DELETE operations |
| `table_count_log` | Row count snapshots |

## SQLAlchemy Models

ORM models live in `db/models/`. The directory is organized by domain:

```
db/models/
├── implementations/
│   ├── agencies.py
│   ├── data_sources.py
│   ├── data_requests.py
│   ├── locations.py
│   ├── users.py
│   ├── links/                  # Link/junction table models
│   │   ├── agency__data_source.py
│   │   └── ...
│   └── ...
└── base.py                     # Base model class
```

## Query Builders

Complex queries are built using `QueryBuilderBase` subclasses instead of inline methods in the DatabaseClient. This is the preferred pattern for new code.

```python
from db.queries.builder.core import QueryBuilderBase

class MyQuery(QueryBuilderBase):
    def run(self):
        # self._session is available here
        stmt = select(MyModel).where(...)
        return self._session.execute(stmt).scalars().all()
```

Query builders are invoked via `DatabaseClient.run_query_builder(MyQuery(...))`.

### CTE/Subquery Wrappers

For reusable CTEs and subqueries, wrap them in classes that expose columns as typed properties:

```python
@final
class AgencyIdsCTE:
    def __init__(self):
        self.query = select(
            func.unnest(LinkAgencyDataSource.agency_id).label("agency_ids"),
            LinkAgencyDataSource.data_source_id,
        ).cte(name="agency_ids")

    @property
    def agency_ids(self) -> list[int]:
        return self.query.c.agency_ids
```

This pattern is documented in detail in [`DESIGN.md`](../../DESIGN.md).

### Query Builder Mixins

Reusable query logic can be shared via mixins — see `db/queries/builder/mixins/` and its [README](../../db/queries/builder/mixins/README.md).

## Alembic Migrations

### Running Migrations

```bash
# Apply all pending migrations
uv run alembic upgrade head

# Downgrade one step
uv run alembic downgrade -1

# See current revision
uv run alembic current

# See migration history
uv run alembic history
```

### Creating a New Migration

```bash
# Auto-generate from model changes
uv run alembic revision --autogenerate -m "description of change"

# Create an empty migration for manual SQL
uv run alembic revision -m "description of change"
```

Migration files are saved to `alembic/versions/` with the naming convention `YYYY_MM_DD_HHMM-{revision}_{slug}.py`.

Alembic is configured with post-write hooks that auto-format generated migrations with ruff.

### Best Practices

- Always test migrations against the local Docker database before pushing.
- CI runs `alembic upgrade head` against a fresh PostgreSQL instance before tests.
- Keep migrations small and focused on a single change.
- Include both `upgrade()` and `downgrade()` functions.

## Local Database Setup

See [Setup: Option A](setup.md#option-a-local-docker-database-recommended-for-schema-work) for Docker-based local database instructions, and the [DataDumper](../../local_database/DataDumper/README.md) for populating it with data.
