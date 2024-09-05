"""
This module provides methods for the dynamic and repeatable running of request middleware logic.
They are designed such that a variety of parameters are provided, and then functionality is
performed in a manner designed to be consistent among all endpoints using them.

"""

from dataclasses import dataclass, field
from http import HTTPStatus
from typing import Optional

from flask import Response

from database_client.database_client import DatabaseClient
from database_client.enums import ColumnPermissionEnum
from middleware.access_logic import AccessInfo
from middleware.column_permission_logic import (
    get_permitted_columns,
    RelationRoleParameters,
    check_has_permission_to_edit_columns,
    get_invalid_columns,
)
from middleware.custom_dataclasses import DeferredFunction
from middleware.common_response_formatting import (
    multiple_results_response,
    created_id_response,
    message_response,
)
from middleware.flask_response_manager import FlaskResponseManager
from middleware.schema_and_dto_logic.response_schemas import EntryDataResponseSchema
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
    # Additional arguments for the Database Client method beyond those provided in the given method
    db_client_additional_args: dict = field(default_factory=dict)
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
        validation_schema=EntryDataResponseSchema,
    )


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
        column_permission=ColumnPermissionEnum.READ,
    )

    permitted_columns = optionally_limit_to_requested_columns(
        permitted_columns,
        requested_columns
    )

    results = mp.db_client_method(
        mp.db_client,
        relation_name=mp.relation,
        columns=permitted_columns,
        page=page,
        **mp.db_client_additional_args,
    )
    return multiple_results_response(message=f"{mp.entry_name} found", data=results)


def optionally_limit_to_requested_columns(
        permitted_columns: list[str],
        requested_columns: Optional[list[str]]
) -> list[str]:
    if requested_columns is not None:
        check_requested_columns(requested_columns, permitted_columns)
        permitted_columns = requested_columns
    return permitted_columns


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
    return created_id_response(new_id=str(id_val), message=f"{mp.entry_name} created.")


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
        FlaskResponseManager.abort(
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
        entry_name=mp.entry_name,
    )

    mp.db_client_method(
        mp.db_client, id_column_name=id_column_name, id_column_value=entry_id
    )
    return message_response(f"{mp.entry_name} deleted.")
