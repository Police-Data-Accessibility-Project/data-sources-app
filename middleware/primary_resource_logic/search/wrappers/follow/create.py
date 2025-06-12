from flask import Response
from werkzeug.exceptions import BadRequest

from db.client import DatabaseClient
from db.models.exceptions import LocationNotFound
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.common_response_formatting import message_response
from middleware.schema_and_dto.dtos.search.request import SearchRequestsDTO


def create_followed_search(
    db_client: DatabaseClient,
    access_info: AccessInfoPrimary,
    dto: SearchRequestsDTO,
) -> Response:
    try:
        db_client.create_followed_search(
            user_id=access_info.get_user_id(),
            location_id=dto.location_id,
            record_types=dto.record_types,
            record_categories=dto.record_categories,
        )
    except LocationNotFound as e:
        raise BadRequest("Location not found.") from e

    return message_response("Location followed.")
