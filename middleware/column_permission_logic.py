from enum import Enum
from http import HTTPStatus

from flask_restx import abort

from database_client.database_client import DatabaseClient
from database_client.enums import RelationRoleEnum, ColumnPermissionEnum


def get_permitted_columns(
    db_client: DatabaseClient,
    relation: str,
    role: RelationRoleEnum,
    column_permission: ColumnPermissionEnum
) -> list[str]:
    return db_client.get_permitted_columns(
        relation=relation,
        role=role,
        column_permission=column_permission
    )

def check_has_permission_to_edit_columns(
    db_client: DatabaseClient,
    relation: str,
    role: RelationRoleEnum,
    columns: list[str]
):
    """
    Checks if the user has permission to edit the given columns
    :param db_client:
    :param relation:
    :param role:
    :param columns:
    :return:
    """
    writeable_columns = get_permitted_columns(
        db_client=db_client,
        relation=relation,
        role=role,
        column_permission=ColumnPermissionEnum.WRITE
    )
    invalid_columns = []
    for column in columns:
        if column not in writeable_columns:
            invalid_columns.append(column)

    if len(invalid_columns) == 0:
        return

    abort(
        code=HTTPStatus.FORBIDDEN,
        message=f"""
        You do not have permission to edit the following columns: 
        {invalid_columns}
        """,
    )