from flask import Response

from db.client.core import DatabaseClient
from middleware.common_response_formatting import message_response
from middleware.schema_and_dto.dtos.data_requests.put import (
    DataRequestsPutOuterDTO,
)
from middleware.security.access_info.primary import AccessInfoPrimary


def update_data_request_wrapper(
    db_client: DatabaseClient,
    dto: DataRequestsPutOuterDTO,
    data_request_id: int,
    access_info: AccessInfoPrimary,
) -> Response:
    db_client.update_data_request_v2(
        data_request_id=data_request_id,
        dto=dto,
        user_id=access_info.get_user_id(),
        permissions=access_info.permissions,
    )
    return message_response(message="Data requests updated.")
