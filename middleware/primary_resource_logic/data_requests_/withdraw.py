from flask import Response
from werkzeug.exceptions import Forbidden

from db.client.core import DatabaseClient
from db.enums import RequestStatus
from middleware.common_response_formatting import message_response
from middleware.primary_resource_logic.data_requests_.helpers import is_creator_or_admin
from middleware.schema_and_dto.dtos.data_requests.put import (
    DataRequestsPutDTO,
    DataRequestsPutOuterDTO,
)
from middleware.security.access_info.primary import AccessInfoPrimary


def withdraw_data_request_wrapper(
    db_client: DatabaseClient, data_request_id: int, access_info: AccessInfoPrimary
) -> Response:
    if not is_creator_or_admin(
        access_info=access_info, data_request_id=data_request_id, db_client=db_client
    ):
        raise Forbidden("User does not have permission to perform this action.")

    db_client.update_data_request_v2(
        dto=DataRequestsPutOuterDTO(
            entry_data=DataRequestsPutDTO(
                request_status=RequestStatus.REQUEST_WITHDRAWN
            )
        ),
        data_request_id=data_request_id,
        bypass_permissions=True,
    )
    return message_response("Data request successfully withdrawn.")
