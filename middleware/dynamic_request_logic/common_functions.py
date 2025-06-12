"""
Contains functions common across multiple dynamic request functions
"""

from http import HTTPStatus

from werkzeug.exceptions import NotFound

from db.client import DatabaseClient
from db.enums import RelationRoleEnum, ColumnPermissionEnum
from middleware.column_permission_logic import get_permitted_columns
from middleware.dynamic_request_logic.supporting_classes import (
    IDInfo,
    MiddlewareParameters,
)
from middleware.flask_response_manager import FlaskResponseManager


def check_for_id(
    table_name: str,
    id_info: IDInfo,
    db_client: DatabaseClient,
):
    """
    Check for existence of ID, aborting if it is not found
    :return:
    """
    result = db_client._select_from_relation(
        relation_name=table_name,
        where_mappings=id_info.where_mappings,
        columns=[id_info.id_column_name],
    )
    if len(result) == 0:
        raise NotFound(f"Entry for {id_info.where_mappings} not found.")

    return result[0][id_info.id_column_name]


def optionally_get_permitted_columns_to_subquery_parameters_(
    mp: MiddlewareParameters, relation_role: RelationRoleEnum
):
    for parameter in mp.subquery_parameters:
        if parameter.columns is None:
            parameter.set_columns(
                get_permitted_columns(
                    relation=parameter.relation_name,
                    role=relation_role,
                    user_permission=ColumnPermissionEnum.READ,
                )
            )
