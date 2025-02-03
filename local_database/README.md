
# TLDR: Setting Up Testing Database

From inside this directory, run:

```python
py setup_local_database.py
```

If dumping, ensure a `.env` file is created in the `DataDumper` directory with the environment variables as described in that directory's `ENV.md` file.

Below is your new database connection environment variable:

```dotenv
DO_DATABASE_URL="postgresql+psycopg://test_data_sources_app_user:ClandestineCornucopiaCommittee@127.0.0.1:5432/test_data_sources_app_db"
```


# Setting Up Test Database

These instructions will help you set up a test PostgreSQL database using Docker Compose.

To set up a test database using Docker Compose, you'll need to have Docker installed and running on your system. You can install docker [here](https://docs.docker.com/engine/install/).

The `docker-compose.yml` file in this directory contains instructions for setting up a test PostgreSQL database using Docker Compose. To start the test database, run the following command:
```bash
docker compose up -d
```

Once the test database is started, make sure to add the following environmental variables to your `.env` file in the root directory of the repository.:
```dotenv
DO_DATABASE_URL="postgresql+psycopg://test_data_sources_app_user:ClandestineCornucopiaCommittee@127.0.0.1:5432/test_data_sources_app_db"
```

To close the test database, run the following command:
```bash
docker compose down
```

# Adding Test Data via DataDumper

Initially, when the database is created, it possesses no data. To add data to the database, you can follow the instructions provided in the [DataDumper](local_database/DataDumper/README.md) directory.