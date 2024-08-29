from flask import Response

from database_client.enums import ColumnPermissionEnum
from middleware.column_permission_logic import get_permitted_columns, RelationRoleParameters, \
    check_has_permission_to_edit_columns
from middleware.custom_dataclasses import MiddlewareParameters, PostParameters, DeferredFunction
from middleware.util import message_response, format_list_response, multiple_results_response, created_id_response


def get_by_id(
    middleware_parameters: MiddlewareParameters,
    id: str,
    relation_role_parameters: RelationRoleParameters = RelationRoleParameters()
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
        where_mappings={"id": id},
    )
    if len(results) == 0:
        return message_response(
            message=f"{mp.entry_name} not found",
        )

    return message_response(
        message=f"{mp.entry_name} found",
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
        mp.db_client,
        relation_name=mp.relation,
        columns=columns,
        page=page
    )
    return multiple_results_response(
        message=f"{mp.entry_name} found",
        data=results
    )

def post_entry(
    middleware_parameters: MiddlewareParameters,
    entry: dict,
    pre_insertion_function_with_parameters: DeferredFunction = None,
    relation_role_parameters: RelationRoleParameters = RelationRoleParameters()
) -> Response:
    mp = middleware_parameters
    relation_role = relation_role_parameters.get_relation_role_from_parameters(
        access_info=mp.access_info,
    )
    check_has_permission_to_edit_columns(
        db_client=mp.db_client,
        relation=mp.relation,
        role=relation_role,
        columns=list(entry.keys())
    )
    if pre_insertion_function_with_parameters is not None:
        pre_insertion_function_with_parameters.execute()

    id_val = mp.db_client_method(
        mp.db_client,
        column_value_mappings=entry
    )
    return created_id_response(
        new_id=id_val,
        message=f"{mp.entry_name} created."
    )