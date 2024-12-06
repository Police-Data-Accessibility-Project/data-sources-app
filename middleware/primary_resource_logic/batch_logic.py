from io import BytesIO

from database_client.database_client import DatabaseClient
from middleware.access_logic import AccessInfoPrimary
from middleware.schema_and_dto_logic.primary_resource_dtos.batch_dtos import BatchRequestDTO
from csv import DictReader

def get_rows_from_csv(
    file: BytesIO
):
    # Get rows from csv
    reader = DictReader(file)
    rows = list(reader)
    return rows



def batch_post_agency(
        db_client: DatabaseClient,
        access_info: AccessInfoPrimary,
        dto: BatchRequestDTO
):

    pass