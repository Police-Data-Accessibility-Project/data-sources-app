from http import HTTPStatus
from typing import Optional

from pydantic import BaseModel, ConfigDict

from database_client.database_client import DatabaseClient
from database_client.enums import RelationRoleEnum, ColumnPermissionEnum
from middleware.access_logic import AccessInfoPrimary
from middleware.custom_dataclasses import DeferredFunction
from middleware.enums import PermissionsEnum, AccessTypeEnum
from middleware.flask_response_manager import FlaskResponseManager

ROLE_COLUMN_PERMISSIONS = {
    "agencies_expanded": {
        "name": {"ADMIN": "READ", "STANDARD": "READ"},
        "submitted_name": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "homepage_url": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "jurisdiction_type": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "state_iso": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "county_fips": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "county_name": {"ADMIN": "READ", "STANDARD": "READ"},
        "lat": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "lng": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "defunct_year": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "agency_type": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "multi_agency": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "no_web_presence": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "airtable_agency_last_modified": {"ADMIN": "READ", "STANDARD": "READ"},
        "approval_status": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "rejection_reason": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "last_approval_editor": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "submitter_contact": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "agency_created": {"ADMIN": "READ", "STANDARD": "READ"},
        "locality_name": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "state_name": {"ADMIN": "READ", "STANDARD": "READ"},
        "id": {"ADMIN": "READ", "STANDARD": "READ"},
    },
    "agencies": {
        "name": {"STANDARD": "READ", "ADMIN": "WRITE"},
        "submitted_name": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "homepage_url": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "jurisdiction_type": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "lat": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "lng": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "defunct_year": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "agency_type": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "multi_agency": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "no_web_presence": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "airtable_agency_last_modified": {"ADMIN": "READ", "STANDARD": "READ"},
        "approval_status": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "rejection_reason": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "last_approval_editor": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "submitter_contact": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "agency_created": {"ADMIN": "READ", "STANDARD": "READ"},
        "county_airtable_uid": {"ADMIN": "READ", "STANDARD": "READ"},
        "location_id": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "id": {"ADMIN": "READ", "STANDARD": "READ"},
        "airtable_uid": {"ADMIN": "NONE", "STANDARD": "NONE"},
    },
    "data_requests": {
        "id": {"ADMIN": "READ", "STANDARD": "READ", "OWNER": "READ"},
        "submission_notes": {"ADMIN": "WRITE", "STANDARD": "READ", "OWNER": "WRITE"},
        "request_status": {"ADMIN": "WRITE", "STANDARD": "READ", "OWNER": "READ"},
        "archive_reason": {"ADMIN": "WRITE", "STANDARD": "NONE", "OWNER": "READ"},
        "date_created": {"ADMIN": "READ", "STANDARD": "READ", "OWNER": "READ"},
        "date_status_last_changed": {
            "ADMIN": "READ",
            "STANDARD": "READ",
            "OWNER": "READ",
        },
        "creator_user_id": {"ADMIN": "READ", "STANDARD": "NONE", "OWNER": "READ"},
        "internal_notes": {"ADMIN": "WRITE", "STANDARD": "NONE", "OWNER": "NONE"},
        "record_types_required": {
            "ADMIN": "WRITE",
            "STANDARD": "READ",
            "OWNER": "READ",
        },
        "pdap_response": {"ADMIN": "WRITE", "STANDARD": "READ", "OWNER": "READ"},
        "coverage_range": {"ADMIN": "WRITE", "STANDARD": "READ", "OWNER": "WRITE"},
        "data_requirements": {"ADMIN": "WRITE", "STANDARD": "READ", "OWNER": "WRITE"},
        "request_urgency": {"ADMIN": "WRITE", "STANDARD": "READ", "OWNER": "WRITE"},
        "title": {"ADMIN": "WRITE", "STANDARD": "READ", "OWNER": "WRITE"},
        "github_issue_number": {"ADMIN": "WRITE", "STANDARD": "READ", "OWNER": "READ"},
        "github_issue_url": {"ADMIN": "WRITE", "STANDARD": "READ", "OWNER": "READ"},
    },
    "data_requests_expanded": {
        "id": {"ADMIN": "READ", "STANDARD": "READ", "OWNER": "READ"},
        "submission_notes": {"ADMIN": "WRITE", "STANDARD": "READ", "OWNER": "WRITE"},
        "request_status": {"ADMIN": "WRITE", "STANDARD": "READ", "OWNER": "READ"},
        "archive_reason": {"ADMIN": "WRITE", "STANDARD": "NONE", "OWNER": "READ"},
        "date_created": {"ADMIN": "READ", "STANDARD": "READ", "OWNER": "READ"},
        "date_status_last_changed": {
            "ADMIN": "READ",
            "STANDARD": "READ",
            "OWNER": "READ",
        },
        "creator_user_id": {"ADMIN": "READ", "STANDARD": "NONE", "OWNER": "READ"},
        "internal_notes": {"ADMIN": "WRITE", "STANDARD": "NONE", "OWNER": "NONE"},
        "record_types_required": {
            "ADMIN": "WRITE",
            "STANDARD": "READ",
            "OWNER": "READ",
        },
        "pdap_response": {"ADMIN": "WRITE", "STANDARD": "READ", "OWNER": "READ"},
        "coverage_range": {"ADMIN": "WRITE", "STANDARD": "READ", "OWNER": "WRITE"},
        "data_requirements": {"ADMIN": "WRITE", "STANDARD": "READ", "OWNER": "WRITE"},
        "request_urgency": {"ADMIN": "WRITE", "STANDARD": "READ", "OWNER": "WRITE"},
        "github_issue_number": {"ADMIN": "WRITE", "STANDARD": "READ", "OWNER": "READ"},
        "github_issue_url": {"ADMIN": "WRITE", "STANDARD": "READ", "OWNER": "READ"},
        "title": {"ADMIN": "WRITE", "STANDARD": "READ", "OWNER": "WRITE"},
    },
    "data_sources_expanded": {
        "name": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "submitted_name": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "description": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "source_url": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "agency_supplied": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "supplying_entity": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "agency_originated": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "agency_aggregation": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "coverage_start": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "coverage_end": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "detail_level": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "data_portal_type": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "record_formats": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "update_method": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "tags": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "readme_url": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "originating_entity": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "retention_schedule": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "scraper_url": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "submission_notes": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "rejection_note": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "last_approval_editor": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "submitter_contact_info": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "agency_described_submitted": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "agency_described_not_in_database": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "data_portal_type_other": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "data_source_request": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "broken_source_url_as_of": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "access_notes": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "url_status": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "approval_status": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "record_type_id": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "record_type_name": {"ADMIN": "READ", "STANDARD": "READ"},
        "access_types": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "updated_at": {"ADMIN": "READ", "STANDARD": "READ"},
        "created_at": {"ADMIN": "READ", "STANDARD": "READ"},
        "id": {"ADMIN": "READ", "STANDARD": "READ"},
        "approval_status_updated_at": {"ADMIN": "READ", "STANDARD": "READ"},
    },
    "data_sources": {
        "name": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "submitted_name": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "description": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "source_url": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "agency_supplied": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "supplying_entity": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "agency_originated": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "agency_aggregation": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "coverage_start": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "coverage_end": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "detail_level": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "data_portal_type": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "record_formats": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "update_method": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "tags": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "readme_url": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "originating_entity": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "retention_schedule": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "scraper_url": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "submission_notes": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "rejection_note": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "last_approval_editor": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "submitter_contact_info": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "agency_described_submitted": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "agency_described_not_in_database": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "data_portal_type_other": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "data_source_request": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "broken_source_url_as_of": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "access_notes": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "url_status": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "approval_status": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "record_type_id": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "access_types": {"ADMIN": "WRITE", "STANDARD": "READ"},
        "updated_at": {"ADMIN": "READ", "STANDARD": "READ"},
        "created_at": {"ADMIN": "READ", "STANDARD": "READ"},
        "id": {"ADMIN": "READ", "STANDARD": "READ"},
        "approval_status_updated_at": {"ADMIN": "READ", "STANDARD": "READ"},
        "airtable_uid": {"ADMIN": "NONE", "STANDARD": "NONE"},
    },
}


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
    db_client: DatabaseClient,
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
        user_permission=ColumnPermissionEnum.WRITE,
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
