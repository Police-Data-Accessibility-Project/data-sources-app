from dataclasses import dataclass
from enum import Enum
from http import HTTPStatus
from typing import Optional

from flask_restx import abort

from database_client.database_client import DatabaseClient
from database_client.enums import RelationRoleEnum, ColumnPermissionEnum
from middleware.access_logic import AccessInfoPrimary
from middleware.custom_dataclasses import DeferredFunction
from middleware.enums import PermissionsEnum, AccessTypeEnum
from middleware.flask_response_manager import FlaskResponseManager


def get_permitted_columns(
    db_client: DatabaseClient,
    relation: str,
    role: RelationRoleEnum,
    column_permission: ColumnPermissionEnum,
) -> list[str]:
    return db_client.get_permitted_columns(
        relation=relation, role=role, column_permission=column_permission
    )


def get_invalid_columns(
    requested_columns: list[str],
    permitted_columns: list[str],
) -> list[str]:
    """
    Returns a list of columns that are not permitted
    :param requested_columns: The columns that were requested
    :param permitted_columns: List of columns that are permitted
    :return:
    """
    invalid_columns = []
    for column in requested_columns:
        if column not in permitted_columns:
            invalid_columns.append(column)
    return invalid_columns


def check_has_permission_to_edit_columns(
    db_client: DatabaseClient, relation: str, role: RelationRoleEnum, columns: list[str]
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
        column_permission=ColumnPermissionEnum.WRITE,
    )
    invalid_columns = get_invalid_columns(
        requested_columns=columns, permitted_columns=writeable_columns
    )
    if len(invalid_columns) == 0:
        return

    FlaskResponseManager.abort(
        code=HTTPStatus.FORBIDDEN,
        message=f"""
        You do not have permission to edit the following columns: 
        {invalid_columns}
        """,
    )


def create_column_permissions_string_table(relation: str):
    """
    Creates a table of column permissions for the given relation
    this is to be displayed in the swagger ui
    :param relation:
    :return:
    """
    db_client = DatabaseClient()
    db_rows = db_client.get_column_permissions_as_permission_table(relation=relation)

    headers = list(db_rows[0].keys())

    # Create the header row
    header_row = " | ".join(headers)
    header_row = f"| {header_row} |"

    # Create the separator row
    separator_row = "|".join(["-" * len(header) for header in headers])
    separator_row = f"|{separator_row}|"

    # Create the data rows
    data_rows = []
    for item in db_rows:
        row = " | ".join(item[key] for key in headers)
        data_rows.append(f"| {row} |")

    # Combine all rows
    table = "\n".join([header_row, separator_row] + data_rows)
    return table


def get_relation_role(access_info: AccessInfoPrimary) -> RelationRoleEnum:
    if access_info.access_type == AccessTypeEnum.API_KEY:
        return RelationRoleEnum.STANDARD
    if PermissionsEnum.DB_WRITE in access_info.permissions:
        return RelationRoleEnum.ADMIN
    return RelationRoleEnum.STANDARD


@dataclass
class RelationRoleParameters:
    relation_role_function_with_params: DeferredFunction = DeferredFunction(
        function=get_relation_role,
    )
    relation_role_override: Optional[RelationRoleEnum] = None

    def get_relation_role_from_parameters(
        self, access_info: AccessInfoPrimary
    ) -> RelationRoleEnum:
        if self.relation_role_override is not None:
            return self.relation_role_override
        return self.relation_role_function_with_params.execute(access_info=access_info)
