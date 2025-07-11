from flask import Response

from db.client.core import DatabaseClient
from middleware.common_response_formatting import created_id_response
from endpoints.instantiations.data_requests_.post.dto import DataRequestsPostDTO
from middleware.security.access_info.primary import AccessInfoPrimary


def create_data_request_wrapper(
    db_client: DatabaseClient, dto: DataRequestsPostDTO, access_info: AccessInfoPrimary
) -> Response:
    dr_id = db_client.create_data_request_v2(dto=dto, user_id=access_info.get_user_id())

    return created_id_response(new_id=str(dr_id), message="Data request created.")
