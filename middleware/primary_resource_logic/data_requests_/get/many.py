from flask import Response

from db.client.core import DatabaseClient
from db.db_client_dataclasses import OrderByParameters
from middleware.dynamic_request_logic.get.many import get_many
from middleware.dynamic_request_logic.supporting_classes import MiddlewareParameters
from middleware.enums import Relations
from middleware.primary_resource_logic.data_requests_.helpers import (
    get_data_requests_subquery_params,
)
from middleware.schema_and_dto.dtos.data_requests.get_many import (
    GetManyDataRequestsRequestsDTO,
)
from middleware.security.access_info.primary import AccessInfoPrimary


def get_data_requests_wrapper(
    db_client: DatabaseClient,
    dto: GetManyDataRequestsRequestsDTO,
    access_info: AccessInfoPrimary,
) -> Response:
    """
    Get data requests
    :param dto:
    :param db_client:
    :param access_info:
    :return:
    """
    db_client_additional_args = {
        "build_metadata": True,
        "order_by": OrderByParameters.construct_from_args(
            sort_by=dto.sort_by, sort_order=dto.sort_order
        ),
        "limit": dto.limit,
    }

    if dto.request_statuses is not None:
        db_client_additional_args["where_mappings"] = {
            "request_status": [rs.value for rs in dto.request_statuses]
        }
    return get_many(
        middleware_parameters=MiddlewareParameters(
            access_info=access_info,
            entry_name="data requests",
            relation=Relations.DATA_REQUESTS_EXPANDED.value,
            db_client_method=DatabaseClient.get_data_requests,
            subquery_parameters=get_data_requests_subquery_params(),
            db_client_additional_args=db_client_additional_args,
        ),
        page=dto.page,
        requested_columns=dto.requested_columns,
    )
