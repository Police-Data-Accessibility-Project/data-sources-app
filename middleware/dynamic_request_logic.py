"""
This module provides methods for the dynamic and repeatable running of request middleware logic.
They are designed such that a variety of parameters are provided, and then functionality is
performed in a manner designed to be consistent among all endpoints using them.
"""
from dataclasses import dataclass
from http import HTTPStatus
from typing import Optional

from flask import Response
from flask_restx import abort

from database_client.database_client import DatabaseClient
from database_client.enums import ColumnPermissionEnum
from middleware.access_logic import AccessInfo
from middleware.column_permission_logic import (
    get_permitted_columns,
    RelationRoleParameters,
    check_has_permission_to_edit_columns,
)
from middleware.custom_dataclasses import DeferredFunction
from middleware.util import (
    message_response,
    multiple_results_response,
    created_id_response, )
from middleware.util_dynamic import call_if_not_none, execute_if_not_none


@dataclass
class MiddlewareParameters:
    """
    Contains parameters for the middleware functions
    """
    access_info: AccessInfo
    relation: str
    db_client_method: callable
    db_client: DatabaseClient = DatabaseClient()
    entry_name: str = "entry"


def get_by_id(
    middleware_parameters: MiddlewareParameters,
    id: str,
    id_column_name: str = "id",
    relation_role_parameters: RelationRoleParameters = RelationRoleParameters(),
) -> Response:
    """
    Get an entry by id
    :param db_client:
    :param relation:
    :param id:
    :param access_info:
    :param relation_role_function:
    :param db_client_method:
    :param relation_role_function_kwargs:
    :return:
    """
    mp = middleware_parameters
    relation_role = relation_role_parameters.get_relation_role_from_parameters(
        access_info=mp.access_info,
    )
    columns = get_permitted_columns(
        db_client=mp.db_client,
        relation=mp.relation,
        role=relation_role,
        column_permission=ColumnPermissionEnum.READ,
    )
    results = mp.db_client_method(
        mp.db_client,
        relation_name=mp.relation,
        columns=columns,
        where_mappings={id_column_name: id},
    )
    return results_dependent_response(mp.entry_name, results)


def results_dependent_response(entry_name: str, results):
    """
    Depending on whether there are results found or not, return different responses
    :param entry_name:
    :param results:
    :return:
    """
    if len(results) == 0:
        return message_response(
            message=f"{entry_name} not found",
        )
    return message_response(
        message=f"{entry_name} found",
        data=results[0],
    )


def get_many(
    middleware_parameters: MiddlewareParameters,
    page: int,
    relation_role_parameters: RelationRoleParameters = RelationRoleParameters(),
) -> Response:
    mp = middleware_parameters
    relation_role = relation_role_parameters.get_relation_role_from_parameters(
        access_info=mp.access_info,
    )
    columns = get_permitted_columns(
        db_client=mp.db_client,
        relation=mp.relation,
        role=relation_role,
        column_permission=ColumnPermissionEnum.READ,
    )
    results = mp.db_client_method(
        mp.db_client, relation_name=mp.relation, columns=columns, page=page
    )
    return multiple_results_response(message=f"{mp.entry_name} found", data=results)


def post_entry(
    middleware_parameters: MiddlewareParameters,
    entry: dict,
    pre_insertion_function_with_parameters: Optional[DeferredFunction] = None,
    relation_role_parameters: RelationRoleParameters = RelationRoleParameters(),
) -> Response:
    mp = middleware_parameters
    relation_role = relation_role_parameters.get_relation_role_from_parameters(
        access_info=mp.access_info,
    )
    check_has_permission_to_edit_columns(
        db_client=mp.db_client,
        relation=mp.relation,
        role=relation_role,
        columns=list(entry.keys()),
    )
    execute_if_not_none(pre_insertion_function_with_parameters)

    id_val = mp.db_client_method(mp.db_client, column_value_mappings=entry)
    return created_id_response(new_id=id_val, message=f"{mp.entry_name} created.")


def put_entry(
    middleware_parameters: MiddlewareParameters,
    entry: dict,
    entry_id: str,
    relation_role_parameters: RelationRoleParameters = RelationRoleParameters(),
) -> Response:
    mp = middleware_parameters
    relation_role = relation_role_parameters.get_relation_role_from_parameters(
        access_info=mp.access_info,
    )
    check_has_permission_to_edit_columns(
        db_client=mp.db_client,
        relation=mp.relation,
        role=relation_role,
        columns=list(entry.keys()),
    )
    mp.db_client_method(
        mp.db_client,
        column_edit_mappings=entry,
        entry_id=entry_id,
    )
    return message_response(message=f"{mp.entry_name} updated.")


def check_for_delete_permissions(check_function: DeferredFunction, entry_name: str):
    if not check_function.execute():
        abort(
            code=HTTPStatus.FORBIDDEN,
            message=f"You do not have permission to delete this {entry_name}.",
        )


def delete_entry(
    middleware_parameters: MiddlewareParameters,
    entry_id: str,
    id_column_name: str = "id",
    permission_checking_function: Optional[DeferredFunction] = None,
):
    mp = middleware_parameters

    call_if_not_none(
        obj=permission_checking_function,
        func=check_for_delete_permissions,
        check_function=permission_checking_function,
        entry_name=mp.entry_name
    )

    mp.db_client_method(
        mp.db_client, id_column_name=id_column_name, id_column_value=entry_id
    )
    return message_response(f"{mp.entry_name} deleted.")
