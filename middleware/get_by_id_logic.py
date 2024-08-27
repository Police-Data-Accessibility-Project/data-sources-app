from database_client.database_client import DatabaseClient
from middleware.access_logic import AccessInfo


def get_by_id(
    db_client: DatabaseClient,
    relation: str,
    id: str,
    access_info: AccessInfo,

)