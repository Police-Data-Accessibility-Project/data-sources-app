from flask import Response

from db.client.core import DatabaseClient
from middleware.column_permission.core import RelationRoleParameters
from middleware.custom_dataclasses import DeferredFunction
from middleware.dynamic_request_logic.get.by_id import get_by_id
from middleware.dynamic_request_logic.supporting_classes import MiddlewareParameters
from middleware.enums import Relations
from middleware.primary_resource_logic.data_requests_.helpers import get_data_requests_subquery_params, \
    get_data_requests_relation_role
from middleware.schema_and_dto.dtos.common.base import GetByIDBaseDTO
from middleware.security.access_info.primary import AccessInfoPrimary


def get_data_request_by_id_wrapper(
    db_client: DatabaseClient, access_info: AccessInfoPrimary, dto: GetByIDBaseDTO
) -> Response:
    """
    Get data requests
    :param dto:
    :param db_client:
    :param access_info:
    :return:
    """
    return get_by_id(
        middleware_parameters=MiddlewareParameters(
            db_client=db_client,
            relation=Relations.DATA_REQUESTS_EXPANDED.value,
            access_info=access_info,
            db_client_method=DatabaseClient.get_data_requests,
            entry_name="Data request",
            subquery_parameters=get_data_requests_subquery_params(),
        ),
        relation_role_parameters=RelationRoleParameters(
            relation_role_function_with_params=DeferredFunction(
                function=get_data_requests_relation_role,
                data_request_id=dto.resource_id,
                db_client=db_client,
            )
        ),
        id=dto.resource_id,
    )
