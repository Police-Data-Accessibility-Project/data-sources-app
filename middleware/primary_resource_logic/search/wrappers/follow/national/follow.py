from db.client import DatabaseClient
from middleware.access_logic import AccessInfoPrimary
from middleware.schema_and_dto.dtos.search.national import (
    SearchFollowNationalRequestDTO,
)


def follow_national_wrapper(
    db_client: DatabaseClient,
    access_info: AccessInfoPrimary,
    dto: SearchFollowNationalRequestDTO,
):
    # If record categories, convert to record types
    ...
