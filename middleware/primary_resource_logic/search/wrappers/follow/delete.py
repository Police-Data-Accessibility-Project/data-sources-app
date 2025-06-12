from flask import Response

from db.client import DatabaseClient
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.common_response_formatting import message_response
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
