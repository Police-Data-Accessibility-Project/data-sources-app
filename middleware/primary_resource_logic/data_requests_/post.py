from flask import Response

from db.client.core import DatabaseClient
from middleware.common_response_formatting import created_id_response
from middleware.schema_and_dto.dtos.data_requests.post import DataRequestsPostDTO
from middleware.security.access_info.primary import AccessInfoPrimary


def create_data_request_wrapper(
    db_client: DatabaseClient, dto: DataRequestsPostDTO, access_info: AccessInfoPrimary
) -> Response:
    # Check that location ids are valid, and get location ids for linking
    location_ids = dto.location_ids if dto.location_ids is not None else []

    column_value_mappings_raw = dict(dto.request_info)
    user_id = access_info.get_user_id()
    column_value_mappings_raw["creator_user_id"] = user_id

    # Insert the data request, get data request id
    dr_id = db_client.create_data_request(
        column_value_mappings=column_value_mappings_raw, column_to_return="id"
    )

    # Insert location ids into linking table
    for location_id in location_ids:
        db_client.create_request_location_relation(
            column_value_mappings={"data_request_id": dr_id, "location_id": location_id}
        )

    # Return data request id
    return created_id_response(new_id=str(dr_id), message="Data request created.")
