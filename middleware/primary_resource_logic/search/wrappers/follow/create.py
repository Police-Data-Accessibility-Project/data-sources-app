from flask import Response

from db.client import DatabaseClient
from middleware.access_logic import AccessInfoPrimary
from middleware.common_response_formatting import message_response
from middleware.dynamic_request_logic.post_logic import post_entry
from middleware.dynamic_request_logic.supporting_classes import MiddlewareParameters
from middleware.enums import Relations
from middleware.primary_resource_logic.search.helpers import (
    get_location_link_and_raise_error_if_not_found,
    FollowedSearchPostLogic,
)
from middleware.schema_and_dto.dtos.search.request import SearchRequestsDTO


def create_followed_search(
    db_client: DatabaseClient,
    access_info: AccessInfoPrimary,
    dto: SearchRequestsDTO,
) -> Response:
    # Get location id. If not found, not a valid location. Raise error
    location_link = get_location_link_and_raise_error_if_not_found(
        db_client=db_client, access_info=access_info, dto=dto
    )
    if location_link.link_id is not None:
        return message_response(
            message="Location already followed.",
        )

    return post_entry(
        middleware_parameters=MiddlewareParameters(
            entry_name="Location for followed search",
            relation=Relations.LINK_USER_FOLLOWED_LOCATION.value,
            db_client_method=DatabaseClient.create_followed_search,
            access_info=access_info,
        ),
        entry={
            "user_id": access_info.get_user_id(),
            "location_id": location_link.location_id,
        },
        check_for_permission=False,
        post_logic_class=FollowedSearchPostLogic,
    )
