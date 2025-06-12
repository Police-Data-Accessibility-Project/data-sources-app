from db.client.core import DatabaseClient


def get_db_client() -> DatabaseClient:
    return DatabaseClient()
