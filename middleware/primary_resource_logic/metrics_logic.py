from database_client.database_client import DatabaseClient


def get_metrics(db_client: DatabaseClient):
    return db_client.get_metrics()
