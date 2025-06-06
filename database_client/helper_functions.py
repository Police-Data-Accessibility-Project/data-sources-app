from database_client.client import DatabaseClient


def get_db_client() -> DatabaseClient:
    return DatabaseClient()
