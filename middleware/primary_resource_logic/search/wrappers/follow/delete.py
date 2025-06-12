from flask import Response

from db.client import DatabaseClient
from middleware.access_logic import AccessInfoPrimary
from middleware.common_response_formatting import message_response
from middleware.dynamic_request_logic.delete import delete_entry
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
    db_client.delete_followed_search(
        user_id=access_info.get_user_id(),
        location_id=dto.location_id,
        record_types=dto.record_types,
        record_categories=dto.record_categories,
    )

    return message_response(message="Unfollowed search.")
