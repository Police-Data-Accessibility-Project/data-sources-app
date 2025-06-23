from typing import Optional

from pydantic import BaseModel, ConfigDict
from werkzeug.exceptions import Forbidden

from db.enums import RelationRoleEnum, ColumnPermissionEnum
from middleware.column_permission.mapping import ROLE_COLUMN_PERMISSIONS
from middleware.custom_dataclasses import DeferredFunction
from middleware.enums import PermissionsEnum, AccessTypeEnum
from middleware.security.access_info.primary import AccessInfoPrimary


def create_column_permissions_string_table(relation: str) -> str:
    permissions = ROLE_COLUMN_PERMISSIONS[relation]
    # Get all unique roles
    roles = sorted({role for perms in permissions.values() for role in perms})

    # Create the header row
    header = "| associated_column | " + " | ".join(roles) + " |"
    separator = "|---" + "|---" * len(roles) + "|"

    # Create rows for each associated column
    rows = []
    for column, perms in permissions.items():
        row = (
            f"| {column} | "
            + " | ".join(perms.get(role, "NONE") for role in roles)
            + " |"
        )
        rows.append(row)

    # Combine everything into a markdown table
    markdown_table = "\n".join([header, separator] + rows)
    return markdown_table


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


def get_relation_role(access_info: AccessInfoPrimary) -> RelationRoleEnum:
    if access_info.access_type == AccessTypeEnum.API_KEY:
        return RelationRoleEnum.STANDARD
    if PermissionsEnum.DB_WRITE in access_info.permissions:
        return RelationRoleEnum.ADMIN
    return RelationRoleEnum.STANDARD


class RelationRoleParameters(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

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
