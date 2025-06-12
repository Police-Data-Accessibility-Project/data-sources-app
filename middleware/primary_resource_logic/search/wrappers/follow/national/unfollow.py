from db.client import DatabaseClient
from middleware.access_logic import AccessInfoPrimary
from middleware.common_response_formatting import message_response
from middleware.schema_and_dto.dtos.search.national import (
    SearchFollowNationalRequestDTO,
)


def unfollow_national_wrapper(
    db_client: DatabaseClient,
    access_info: AccessInfoPrimary,
    dto: SearchFollowNationalRequestDTO,
):
    # If record categories, convert to record types
    national_location_id = db_client.get_national_location_id()
    db_client.delete_followed_search(
        user_id=access_info.get_user_id(),
        location_id=national_location_id,
        record_types=dto.record_types,
        record_categories=dto.record_categories,
    )

    return message_response(message="Unfollowed national search.")
