from http import HTTPStatus
from typing import Optional

from flask import Response

from database_client.enums import ColumnPermissionEnum, RelationRoleEnum
from database_client.subquery_logic import SubqueryParameters
from middleware.column_permission_logic import (
    RelationRoleParameters,
    get_permitted_columns,
    get_invalid_columns,
)
from middleware.common_response_formatting import multiple_results_response
from middleware.dynamic_request_logic.common_functions import (
    optionally_get_permitted_columns_to_subquery_parameters_,
)
from middleware.dynamic_request_logic.supporting_classes import MiddlewareParameters
from middleware.flask_response_manager import FlaskResponseManager


def get_many(
    middleware_parameters: MiddlewareParameters,
    page: int,
    relation_role_parameters: RelationRoleParameters = RelationRoleParameters(),
    requested_columns: Optional[list[str]] = None,
) -> Response:
    """

    :param middleware_parameters:
    :param page:
    :param relation_role_parameters:
    :param requested_columns: Optional list of strings representing columns to return
    :return:
    """
    mp = middleware_parameters
    relation_role = relation_role_parameters.get_relation_role_from_parameters(
        access_info=mp.access_info,
    )
    permitted_columns = get_permitted_columns(
        db_client=mp.db_client,
        relation=mp.relation,
        role=relation_role,
        user_permission=ColumnPermissionEnum.READ,
    )

    permitted_columns = optionally_limit_to_requested_columns(
        permitted_columns, requested_columns
    )

    process_subquery_parameters(requested_columns, relation_role, mp)

    results = mp.db_client_method(
        mp.db_client,
        relation_name=mp.relation,
        columns=permitted_columns,
        page=page,
        subquery_parameters=mp.subquery_parameters,
        **mp.db_client_additional_args,
    )
    return multiple_results_response(message=f"{mp.entry_name} found", data=results)


def optionally_limit_to_requested_columns(
    permitted_columns: list[str], requested_columns: Optional[list[str]]
) -> list[str]:
    if requested_columns is not None:
        check_requested_columns(requested_columns, permitted_columns)
        permitted_columns = requested_columns
    return permitted_columns


def process_subquery_parameters(
    requested_columns: list[str],
    relation_role: RelationRoleEnum,
    mp: MiddlewareParameters,
):
    if requested_columns is None:
        optionally_get_permitted_columns_to_subquery_parameters_(
            mp=mp,
            relation_role=relation_role,
        )
    else:
        mp.subquery_parameters = []


def check_requested_columns(requested_columns: list[str], permitted_columns: list[str]):
    """
    Checks to see if all requested columns are permitted columns
     and aborts if not
    :param requested_columns:
    :param permitted_columns:
    :return: None
    """
    invalid_columns = get_invalid_columns(requested_columns, permitted_columns)
    if len(invalid_columns) > 0:
        FlaskResponseManager.abort(
            code=HTTPStatus.FORBIDDEN,
            message=f"The following columns are either invalid or not permitted for your access permissions: {invalid_columns}",
        )
