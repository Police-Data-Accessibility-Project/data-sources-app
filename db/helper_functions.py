from db.client import DatabaseClient


def get_db_client() -> DatabaseClient:
    return DatabaseClient()
