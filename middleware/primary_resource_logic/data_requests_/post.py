from flask import Response

from db.client.core import DatabaseClient
from middleware.common_response_formatting import created_id_response
from middleware.schema_and_dto.dtos.data_requests.post import DataRequestsPostDTO
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.third_party_interaction_logic.mailgun_.constants import OPERATIONS_EMAIL
from middleware.third_party_interaction_logic.mailgun_.send import send_via_mailgun


def create_data_request_wrapper(
    db_client: DatabaseClient, dto: DataRequestsPostDTO, access_info: AccessInfoPrimary
) -> Response:
    dr_id = db_client.create_data_request_v2(dto=dto, user_id=access_info.get_user_id())

    send_via_mailgun(
        to_email=OPERATIONS_EMAIL,
        subject=f"New data request submitted: {dto.request_info.title}",
        text=f"Submission notes: \n\n{dto.request_info.submission_notes}",
    )

    return created_id_response(new_id=str(dr_id), message="Data request created.")
