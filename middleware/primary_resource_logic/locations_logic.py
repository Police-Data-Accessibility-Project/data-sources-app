from http import HTTPStatus

from flask import Response

from database_client.database_client import DatabaseClient
from database_client.enums import ColumnPermissionEnum
from middleware.access_logic import AccessInfoPrimary
from middleware.column_permission_logic import get_permitted_columns, get_relation_role
from middleware.common_response_formatting import (
    message_response,
    multiple_results_response,
)
from middleware.dynamic_request_logic.get_many_logic import get_many
from middleware.dynamic_request_logic.get_related_resource_logic import (
    get_related_resource,
    GetRelatedResourcesParameters,
)
from middleware.dynamic_request_logic.supporting_classes import MiddlewareParameters
from middleware.enums import Relations
from middleware.flask_response_manager import FlaskResponseManager
from middleware.primary_resource_logic.data_requests import (
    get_data_requests_subquery_params,
)
from middleware.schema_and_dto_logic.common_schemas_and_dtos import GetByIDBaseDTO


def get_location_by_id_wrapper(db_client: DatabaseClient, location_id: int) -> Response:
    result = db_client.get_location_by_id(location_id=location_id)
    if result is None:
        return message_response(
            message="Location not found.", status_code=HTTPStatus.BAD_REQUEST
        )
    return FlaskResponseManager.make_response(data=result)


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
            db_client=db_client,
            relation=Relations.DATA_REQUESTS_EXPANDED.value,
            role=get_relation_role(access_info=access_info),
            column_permission=ColumnPermissionEnum.READ,
        ),
    )
    if results is None:
        return message_response(
            message="Location not found or no data requests found.",
            status_code=HTTPStatus.BAD_REQUEST,
        )
    return multiple_results_response(message="Data requests found.", data=results)
