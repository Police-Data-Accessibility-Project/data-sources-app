from werkzeug.exceptions import Forbidden

from db.enums import RelationRoleEnum, ColumnPermissionEnum
from middleware.column_permission.mapping import ROLE_COLUMN_PERMISSIONS


def get_permitted_columns(
    relation: str,
    role: RelationRoleEnum,
    user_permission: ColumnPermissionEnum,
) -> list[str]:
    columns_for_permission = []
    all_columns = ROLE_COLUMN_PERMISSIONS[relation]
    for column_name, column_permissions in all_columns.items():
        role_permission = column_permissions[role.value]
        approved = False
        if user_permission.value == "WRITE":
            # User can only write to columns marked as WRITE
            if role_permission == "WRITE":
                approved = True
        elif user_permission.value == "READ":
            # Use can read any column not marked as NONE
            if role_permission != "NONE":
                approved = True
        if approved:
            columns_for_permission.append(column_name)

    return columns_for_permission


def get_invalid_columns(
    requested_columns: list[str],
    permitted_columns: list[str],
) -> list[str]:
    """
    Returns a list of columns that are not permitted
    :param requested_columns: The columns that were requested
    :param permitted_columns: List of columns that are permitted
    """
    invalid_columns = []
    for column in requested_columns:
        if column not in permitted_columns:
            invalid_columns.append(column)
    return invalid_columns


def check_has_permission_to_edit_columns(
    relation: str, role: RelationRoleEnum, columns: list[str]
):
    """Checks if the user has permission to edit the given columns."""
    writeable_columns = get_permitted_columns(
        relation=relation,
        role=role,
        user_permission=ColumnPermissionEnum.WRITE,
    )
    invalid_columns = get_invalid_columns(
        requested_columns=columns, permitted_columns=writeable_columns
    )
    if len(invalid_columns) == 0:
        return

    raise Forbidden(
        f"""
        You do not have permission to edit the following columns: 
        {invalid_columns}
        """
    )
