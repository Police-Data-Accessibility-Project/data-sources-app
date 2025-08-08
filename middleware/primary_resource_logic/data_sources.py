import os

from typing import Optional

from flask import make_response, Response
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest

from db.client.core import DatabaseClient
from db.db_client_dataclasses import OrderByParameters
from db.enums import ApprovalStatus, RelationRoleEnum, ColumnPermissionEnum
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.column_permission.core import get_permitted_columns
from middleware.dynamic_request_logic.delete import delete_entry
from middleware.dynamic_request_logic.get.many import (
    optionally_limit_to_requested_columns,
)

from middleware.dynamic_request_logic.post import (
    PostLogic,
)
from middleware.dynamic_request_logic.supporting_classes import (
    MiddlewareParameters,
    IDInfo,
)

from middleware.enums import Relations, PermissionsEnum
from middleware.schema_and_dto.dtos.data_requests.by_id.source import (
    RelatedSourceByIDDTO,
)
from middleware.schema_and_dto.dtos.entry_create_update_request import (
    EntryCreateUpdateRequestDTO,
)
from middleware.schema_and_dto.dtos.common.base import (
    GetManyBaseDTO,
    GetByIDBaseDTO,
)
from middleware.common_response_formatting import message_response
from middleware.schema_and_dto.dtos.data_sources.post import DataSourcesPostDTO
from middleware.schema_and_dto.dtos.data_sources.reject import (
    DataSourcesRejectDTO,
)
from middleware.third_party_interaction_logic.mailgun_.constants import OPERATIONS_EMAIL
from middleware.third_party_interaction_logic.mailgun_.send import send_via_mailgun

RELATION = Relations.DATA_SOURCES.value


class DataSourcesGetManyRequestDTO(GetManyBaseDTO):
    approval_status: ApprovalStatus = ApprovalStatus.APPROVED
    page_number: int = 1


class DataSourcesColumnRequestObject(BaseModel):
    data_sources_columns: list[str]
    data_requests_columns: list[str]


def get_data_sources_columns(
    access_info: AccessInfoPrimary, requested_columns: Optional[list[str]] = None
) -> DataSourcesColumnRequestObject:
    requested_columns = requested_columns

    if access_info.has_permission(PermissionsEnum.DB_WRITE):
        role = RelationRoleEnum.ADMIN
    else:
        role = RelationRoleEnum.STANDARD

    data_requests_columns = get_permitted_columns(
        relation=Relations.DATA_REQUESTS.value,
        role=role,
        user_permission=ColumnPermissionEnum.READ,
    )

    # Data sources columns are also variable depending on permission,
    # but are also potentially limited by requested columns
    data_sources_columns = optionally_limit_to_requested_columns(
        permitted_columns=get_permitted_columns(
            relation=Relations.DATA_SOURCES_EXPANDED.value,
            role=role,
            user_permission=ColumnPermissionEnum.READ,
        ),
        requested_columns=requested_columns,
    )

    return DataSourcesColumnRequestObject(
        data_sources_columns=data_sources_columns,
        data_requests_columns=data_requests_columns,
    )


def get_data_sources_wrapper(
    db_client: DatabaseClient,
    access_info: AccessInfoPrimary,
    dto: DataSourcesGetManyRequestDTO,
) -> Response:
    cro: DataSourcesColumnRequestObject = get_data_sources_columns(
        access_info=access_info, requested_columns=dto.requested_columns
    )

    results = db_client.get_data_sources(
        data_sources_columns=cro.data_sources_columns,
        data_requests_columns=cro.data_requests_columns,
        order_by=OrderByParameters.construct_from_args(
            sort_by=dto.sort_by, sort_order=dto.sort_order
        ),
        approval_status=dto.approval_status,
        page=dto.page,
        limit=dto.limit,
    )

    return make_response(
        {
            "metadata": {"count": len(results)},
            "message": "Successfully retrieved data sources",
            "data": results,
        }
    )


def delete_data_source_wrapper(
    db_client: DatabaseClient,
    access_info: AccessInfoPrimary,
    data_source_id: str,
) -> Response:
    return delete_entry(
        middleware_parameters=MiddlewareParameters(
            access_info=access_info,
            relation=RELATION,
            db_client_method=DatabaseClient.delete_data_source,
            entry_name="data source",
        ),
        id_info=IDInfo(
            id_column_name="id",
            id_column_value=int(data_source_id),
        ),
    )


def update_data_source_wrapper(
    db_client: DatabaseClient,
    dto: EntryCreateUpdateRequestDTO,
    access_info: AccessInfoPrimary,
    data_source_id: str,
) -> Response:
    try:
        db_client.update_data_source_v2(
            dto=dto,
            data_source_id=int(data_source_id),
            permissions=access_info.permissions,
            user_id=access_info.get_user_id(),
        )
    except IntegrityError as e:
        if "check_for_approval_status_and_record_type_id" in str(e):
            raise BadRequest("Record type is required for approval.")
    return message_response("Updated Data source.")


def add_new_data_source_wrapper(
    db_client: DatabaseClient, dto: DataSourcesPostDTO, access_info: AccessInfoPrimary
) -> Response:
    data_source_id = db_client.add_data_source_v2(dto)

    # Only send email if notifications are enabled
    if os.getenv("SEND_OPS_NOTIFICATIONS", "false").lower() == "true":
        send_via_mailgun(
            to_email=OPERATIONS_EMAIL,
            subject=f"New data source submitted: {dto.entry_data.name}",
            text=f"Description: \n\n{dto.entry_data.description}",
        )

    return make_response(
        {
            "id": str(data_source_id),
            "message": "Successfully added data source.",
        }
    )


# region Related Resources


def get_data_source_related_agencies(
    db_client: DatabaseClient, dto: GetByIDBaseDTO
) -> Response:
    results = db_client.get_data_source_related_agencies(
        data_source_id=int(dto.resource_id)
    )
    if results is None:
        return message_response("Data Source not found.")

    return make_response(
        {
            "metadata": {"count": len(results)},
            "message": "Successfully retrieved related agencies",
            "data": results,
        }
    )


class CreateDataSourceRelatedAgenciesLogic(PostLogic):
    def make_response(self) -> Response:
        return message_response("Agency successfully associated with data source.")


def create_data_source_related_agency(
    db_client: DatabaseClient,
    access_info: AccessInfoPrimary,
    dto: RelatedSourceByIDDTO,
) -> Response:
    post_logic = CreateDataSourceRelatedAgenciesLogic(
        middleware_parameters=MiddlewareParameters(
            access_info=access_info,
            entry_name="Data source-agency association",
            relation=RELATION,
            db_client_method=DatabaseClient.create_data_source_agency_relation,
        ),
        entry=dto.get_where_mapping(),
        check_for_permission=False,
    )
    return post_logic.execute()


def delete_data_source_related_agency(
    db_client: DatabaseClient,
    access_info: AccessInfoPrimary,
    dto: RelatedSourceByIDDTO,
) -> Response:
    return delete_entry(
        middleware_parameters=MiddlewareParameters(
            access_info=access_info,
            entry_name="Data source-agency association",
            relation=Relations.LINK_AGENCIES_DATA_SOURCES.value,
            db_client_method=DatabaseClient.delete_data_source_agency_relation,
        ),
        id_info=IDInfo(
            additional_where_mappings=dto.get_where_mapping(),
        ),
    )


# endregion


# region Reject Data Source
def reject_data_source(
    db_client: DatabaseClient,
    dto: DataSourcesRejectDTO,
) -> Response:
    db_client.reject_data_source(
        data_source_id=int(dto.resource_id), rejection_note=dto.rejection_note
    )
    return message_response("Successfully rejected data source.")


# endregion
