from typing import Optional

from flask import make_response, Response
from pydantic import BaseModel

from db.client.core import DatabaseClient
from db.db_client_dataclasses import OrderByParameters
from db.enums import ApprovalStatus, RelationRoleEnum, ColumnPermissionEnum
from middleware.column_permission.core import get_permitted_columns
from middleware.dynamic_request_logic.get.many import (
    optionally_limit_to_requested_columns,
)
from middleware.enums import Relations, PermissionsEnum
from middleware.schema_and_dto.dtos.common.base import (
    GetManyBaseDTO,
)
from middleware.security.access_info.primary import AccessInfoPrimary

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
