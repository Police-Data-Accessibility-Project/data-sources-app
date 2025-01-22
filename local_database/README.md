

# Setting Up Test Database

To perform the following tests, you'll need to set up a test PostgreSQL database using Docker Compose.

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