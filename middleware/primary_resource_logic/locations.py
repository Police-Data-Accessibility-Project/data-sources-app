from flask import Response, make_response
from werkzeug.exceptions import BadRequest

from db.client.core import DatabaseClient
from db.enums import ColumnPermissionEnum
from middleware.column_permission.core import get_permitted_columns
from middleware.security.access_info.helpers import get_relation_role
from middleware.common_response_formatting import (
    multiple_results_response,
)
from middleware.enums import Relations
from middleware.primary_resource_logic.data_requests_.helpers import (
    get_data_requests_subquery_params,
)
from middleware.schema_and_dto.dtos.common.base import GetByIDBaseDTO
from middleware.schema_and_dto.dtos.locations.get import LocationsGetRequestDTO
from middleware.security.access_info.primary import AccessInfoPrimary


def get_location_by_id_wrapper(db_client: DatabaseClient, location_id: int) -> Response:
    result = db_client.get_location_by_id(location_id=location_id)
    if result is None:
        raise BadRequest("Location not found.")
    return make_response(result)


def get_many_locations_wrapper(
    db_client: DatabaseClient, dto: LocationsGetRequestDTO
) -> Response:
    return make_response(
        {
            "results": db_client.get_many_locations(
                page=dto.page, has_coordinates=dto.has_coordinates, type_=dto.type
            ),
        }
    )


def get_locations_related_data_requests_wrapper(
    db_client: DatabaseClient, access_info: AccessInfoPrimary, dto: GetByIDBaseDTO
) -> Response:
    results = db_client.get_linked_rows(
        link_table=Relations.LINK_LOCATIONS_DATA_REQUESTS,
        left_id=int(dto.resource_id),
        left_link_column="location_id",
        right_link_column="data_request_id",
        linked_relation=Relations.DATA_REQUESTS_EXPANDED,
        linked_relation_linking_column="id",
        columns_to_retrieve=get_permitted_columns(
            relation=Relations.DATA_REQUESTS_EXPANDED.value,
            role=get_relation_role(access_info=access_info),
            user_permission=ColumnPermissionEnum.READ,
        ),
        build_metadata=True,
        subquery_parameters=get_data_requests_subquery_params(),
    )
    if results is None:
        raise BadRequest("Location not found or no data requests found.")

    return multiple_results_response(message="Data requests found.", data=results)
