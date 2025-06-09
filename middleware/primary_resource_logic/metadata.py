from db.client import DatabaseClient


def get_record_types_and_categories(
    db_client: DatabaseClient,
):
    return db_client.get_record_types_and_categories()
