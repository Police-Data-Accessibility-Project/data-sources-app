from flask import Response

from db.client import DatabaseClient
from middleware.access_logic import AccessInfoPrimary
from middleware.common_response_formatting import message_response
from middleware.dynamic_request_logic.delete_logic import delete_entry
from middleware.dynamic_request_logic.supporting_classes import (
    MiddlewareParameters,
    IDInfo,
)
from middleware.enums import Relations
from middleware.primary_resource_logic.search.helpers import (
    get_location_link_and_raise_error_if_not_found,
)
from middleware.schema_and_dto.dtos.search.request import SearchRequestsDTO


def delete_followed_search(
    db_client: DatabaseClient,
    access_info: AccessInfoPrimary,
    dto: SearchRequestsDTO,
) -> Response:
    # Get location id. If not found, not a valid location. Raise error
    location_link = get_location_link_and_raise_error_if_not_found(
        db_client=db_client, access_info=access_info, dto=dto
    )
    # Check if search is followed. If not, end early .
    if location_link.link_id is None:
        return message_response(
            message="Location not followed.",
        )

    return delete_entry(
        middleware_parameters=MiddlewareParameters(
            entry_name="Location for followed search",
            relation=Relations.LINK_USER_FOLLOWED_LOCATION.value,
            db_client_method=DatabaseClient.delete_followed_search,
            access_info=access_info,
        ),
        id_info=IDInfo(
            id_column_name="id",
            id_column_value=location_link.link_id,
        ),
    )
