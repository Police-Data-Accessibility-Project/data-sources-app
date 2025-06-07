from http import HTTPStatus

from flask import Response

from db.client import DatabaseClient
from db.enums import ColumnPermissionEnum
from db.exceptions import LocationDoesNotExistError
from middleware.access_logic import AccessInfoPrimary
from middleware.column_permission_logic import get_permitted_columns, get_relation_role
from middleware.common_response_formatting import (
    message_response,
    multiple_results_response,
)
from middleware.enums import Relations
from middleware.flask_response_manager import FlaskResponseManager
from middleware.primary_resource_logic.data_requests import (
    get_data_requests_subquery_params,
)

from middleware.schema_and_dto_logic.common_schemas_and_dtos import GetByIDBaseDTO
from middleware.schema_and_dto_logic.dtos.locations_dtos import (
    LocationPutDTO,
    LocationsGetRequestDTO,
)


def get_location_by_id_wrapper(db_client: DatabaseClient, location_id: int) -> Response:
    result = db_client.get_location_by_id(location_id=location_id)
    if result is None:
        return message_response(
            message="Location not found.", status_code=HTTPStatus.BAD_REQUEST
        )
    return FlaskResponseManager.make_response(data=result)


def get_many_locations_wrapper(
    db_client: DatabaseClient, dto: LocationsGetRequestDTO
) -> Response:
    return FlaskResponseManager.make_response(
        data={
            "results": db_client.get_many_locations(
                page=dto.page, has_coordinates=dto.has_coordinates, type_=dto.type
            ),
        }
    )


def update_location_by_id_wrapper(
    db_client: DatabaseClient,
    dto: LocationPutDTO,
    location_id: int,
) -> Response:
    try:
        db_client.update_location_by_id(location_id=int(location_id), dto=dto)
    except LocationDoesNotExistError:
        return message_response(
            message="Location not found.", status_code=HTTPStatus.BAD_REQUEST
        )
    return message_response(
        message="Successfully updated location.", status_code=HTTPStatus.OK
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
        return message_response(
            message="Location not found or no data requests found.",
            status_code=HTTPStatus.BAD_REQUEST,
        )
    return multiple_results_response(message="Data requests found.", data=results)


def get_locations_for_map_wrapper(db_client: DatabaseClient) -> Response:
    return FlaskResponseManager.make_response(
        data={
            "localities": db_client.get_map_localities(),
            "counties": db_client.get_map_counties(),
            "states": db_client.get_map_states(),
        }
    )
