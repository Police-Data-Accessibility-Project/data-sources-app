"""
Contains functions common across multiple dynamic request functions
"""

from http import HTTPStatus

from database_client.database_client import DatabaseClient
from middleware.dynamic_request_logic.supporting_classes import IDInfo
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
        FlaskResponseManager.abort(
            code=HTTPStatus.NOT_FOUND,
            message=f"Entry for {id_info.where_mappings} not found.",
        )
    return result[0][id_info.id_column_name]
