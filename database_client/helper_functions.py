from database_client.database_client import DatabaseClient


def get_db_client() -> DatabaseClient:
    return DatabaseClient()
