from db.client import DatabaseClient
from db.enums import ApprovalStatus
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.common_response_formatting import created_id_response
from middleware.schema_and_dto.dtos.agencies.post import AgenciesPostDTO


def propose_agency(
    db_client: DatabaseClient, access_info: AccessInfoPrimary, dto: AgenciesPostDTO
):
    dto.agency_info.approval_status = ApprovalStatus.PENDING
    agency_id = db_client.create_agency(dto, user_id=access_info.user_id)

    return created_id_response(
        new_id=str(agency_id), message=f"Agency proposal created."
    )
