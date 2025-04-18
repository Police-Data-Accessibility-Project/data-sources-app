from database_client.database_client import DatabaseClient
from database_client.enums import ApprovalStatus
from middleware.access_logic import AccessInfoPrimary
from middleware.common_response_formatting import created_id_response
from middleware.schema_and_dto_logic.primary_resource_dtos.agencies_dtos import (
    AgenciesPostDTO,
)


def propose_agency(
    db_client: DatabaseClient, access_info: AccessInfoPrimary, dto: AgenciesPostDTO
):
    dto.agency_info.approval_status = ApprovalStatus.PENDING
    agency_id = db_client.create_agency(dto, user_id=access_info.user_id)

    return created_id_response(
        new_id=str(agency_id), message=f"Agency proposal created."
    )
