from flask import Response

from db.client.core import DatabaseClient
from middleware.custom_dataclasses import DeferredFunction
from middleware.dynamic_request_logic.delete import delete_entry
from middleware.dynamic_request_logic.supporting_classes import (
    MiddlewareParameters,
    IDInfo,
)
from middleware.primary_resource_logic.data_requests_.constants import RELATION
from middleware.primary_resource_logic.data_requests_.helpers import is_creator_or_admin
from middleware.security.access_info.primary import AccessInfoPrimary


def delete_data_request_wrapper(
    db_client: DatabaseClient, data_request_id: int, access_info: AccessInfoPrimary
) -> Response:
    """
    Delete data requests
    :param db_client:
    :param access_info:
    :return:
    """
    return delete_entry(
        middleware_parameters=MiddlewareParameters(
            access_info=access_info,
            entry_name="Data request",
            relation=RELATION,
            db_client_method=DatabaseClient.delete_data_request,
        ),
        id_info=IDInfo(id_column_value=data_request_id),
        permission_checking_function=DeferredFunction(
            is_creator_or_admin,
            access_info=access_info,
            data_request_id=data_request_id,
            db_client=db_client,
        ),
    )
