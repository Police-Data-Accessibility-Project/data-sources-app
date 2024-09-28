"""
This module provides methods for the dynamic and repeatable running of request middleware logic.
They are designed such that a variety of parameters are provided, and then functionality is
performed in a manner designed to be consistent among all endpoints using them.

"""

from typing import Optional

from flask import Response

from database_client.enums import ColumnPermissionEnum
from database_client.db_client_dataclasses import WhereMapping
from middleware.column_permission_logic import (
    get_permitted_columns,
    RelationRoleParameters,
)
from middleware.common_response_formatting import (
    message_response,
)
from middleware.dynamic_request_logic.common_functions import check_for_id
from middleware.dynamic_request_logic.supporting_classes import (
    MiddlewareParameters,
    IDInfo,
)
from middleware.schema_and_dto_logic.response_schemas import EntryDataResponseSchema


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


def get_by_id(
    middleware_parameters: MiddlewareParameters,
    id: str,
    id_column_name: str = "id",
    relation_role_parameters: RelationRoleParameters = RelationRoleParameters(),
) -> Response:
    """
    Get an entry by id
    """
    try:
        id = int(id)
    except ValueError:
        pass

    mp = middleware_parameters
    check_for_id(
        db_client=mp.db_client,
        table_name=mp.relation,
        id_info=IDInfo(
            id_column_value=id,
            id_column_name=id_column_name,
        ),
    )
    relation_role = relation_role_parameters.get_relation_role_from_parameters(
        access_info=mp.access_info,
    )
    columns = get_permitted_columns(
        db_client=mp.db_client,
        relation=mp.relation,
        role=relation_role,
        column_permission=ColumnPermissionEnum.READ,
    )
    [
        parameter.set_columns(
            get_permitted_columns(
                db_client=mp.db_client,
                relation=parameter.relation_name,
                role=relation_role,
                column_permission=ColumnPermissionEnum.READ,
            )
        )
        for parameter in mp.subquery_params
    ]
    results = mp.db_client_method(
        mp.db_client,
        relation_name=mp.relation,
        columns=columns,
        where_mappings=[WhereMapping(column=id_column_name, value=id)],
        subquery_parameters=mp.subquery_params
    )
    return results_dependent_response(mp.entry_name, results)
