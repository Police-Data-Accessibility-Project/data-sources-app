from http import HTTPStatus
from typing import List, Optional

from flask import make_response, Response
from pydantic import BaseModel

from database_client.database_client import DatabaseClient
from database_client.db_client_dataclasses import OrderByParameters
from database_client.subquery_logic import SubqueryParameterManager
from database_client.enums import ApprovalStatus, RelationRoleEnum, ColumnPermissionEnum
from database_client.result_formatter import ResultFormatter
from middleware.access_logic import AccessInfoPrimary
from middleware.column_permission_logic import get_permitted_columns
from middleware.dynamic_request_logic.delete_logic import delete_entry
from middleware.dynamic_request_logic.get_many_logic import (
    optionally_limit_to_requested_columns,
)

from middleware.dynamic_request_logic.post_logic import (
    PostLogic,
    PostHandler,
    post_entry_with_handler,
)
from middleware.dynamic_request_logic.put_logic import put_entry, PutHandler
from middleware.dynamic_request_logic.supporting_classes import (
    MiddlewareParameters,
    IDInfo,
    PutPostRequestInfo,
)

from middleware.enums import Relations, PermissionsEnum
from middleware.flask_response_manager import FlaskResponseManager
from middleware.schema_and_dto_logic.primary_resource_dtos.data_requests_dtos import (
    RelatedSourceByIDDTO,
)
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    GetManyBaseDTO,
    EntryCreateUpdateRequestDTO,
    GetByIDBaseDTO,
)
from middleware.common_response_formatting import format_list_response, message_response
from middleware.schema_and_dto_logic.primary_resource_dtos.data_sources_dtos import (
    DataSourcesPostDTO,
    DataSourcesPutDTO,
    DataSourcesRejectDTO,
)
from middleware.util.type_conversion import dataclass_to_filtered_dict

RELATION = Relations.DATA_SOURCES.value
SUBQUERY_PARAMS = [
    SubqueryParameterManager.agencies(),
    SubqueryParameterManager.data_requests(),
]


class DataSourceNotFoundError(Exception):
    pass


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

    return FlaskResponseManager.make_response(
        data={
            "metadata": {"count": len(results)},
            "message": "Successfully retrieved data sources",
            "data": results,
        }
    )


def data_source_by_id_wrapper(
    db_client: DatabaseClient, access_info: AccessInfoPrimary, dto: GetByIDBaseDTO
) -> Response:

    cro: DataSourcesColumnRequestObject = get_data_sources_columns(
        access_info=access_info,
    )

    result = db_client.get_data_source_by_id(
        int(dto.resource_id),
        data_requests_columns=cro.data_requests_columns,
        data_sources_columns=cro.data_sources_columns,
    )

    return FlaskResponseManager.make_response(
        data={
            "data": result,
            "message": "Successfully retrieved data source",
        }
    )


def get_data_sources_for_map_wrapper(db_client: DatabaseClient) -> Response:
    raw_results = db_client.get_data_sources_for_map()
    zipped_results = ResultFormatter.zip_get_datas_sources_for_map_results(raw_results)
    return make_response(
        format_list_response(
            data={"data": zipped_results},
        ),
        HTTPStatus.OK.value,
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


def optionally_add_last_approval_editor(
    entry_data: dict, access_info: AccessInfoPrimary
):
    if "approval_status" in entry_data:
        entry_data["last_approval_editor"] = access_info.get_user_id()


def update_data_source_wrapper(
    db_client: DatabaseClient,
    dto: EntryCreateUpdateRequestDTO,
    access_info: AccessInfoPrimary,
    data_source_id: str,
) -> Response:
    entry_data = dto.entry_data
    optionally_swap_record_type_name_with_id(db_client, entry_data)
    optionally_add_last_approval_editor(entry_data, access_info)
    return put_entry(
        middleware_parameters=MiddlewareParameters(
            entry_name="Data source",
            relation=RELATION,
            db_client_method=DatabaseClient.update_data_source,
            access_info=access_info,
        ),
        entry=entry_data,
        entry_id=data_source_id,
    )


def optionally_swap_record_type_name_with_id(db_client, entry_data):
    if "record_type_name" in entry_data:
        record_type_id = db_client.get_record_type_id_by_name(
            record_type_name=entry_data["record_type_name"]
        )
        entry_data["record_type_id"] = record_type_id
        del entry_data["record_type_name"]


class DataSourcesPostLogic(PostLogic):
    def __init__(
        self,
        middleware_parameters: MiddlewareParameters,
        entry: dict,
        agency_ids: Optional[List[int]] = None,
    ):
        super().__init__(
            middleware_parameters=middleware_parameters,
            entry=entry,
            check_for_permission=False,
        )
        self.agency_ids = agency_ids

    def post_database_client_method_logic(self):
        if self.agency_ids is None:
            return
        for agency_id in self.agency_ids:
            self.mp.db_client.create_data_source_agency_relation(
                column_value_mappings={
                    "data_source_id": self.id_val,
                    "agency_id": agency_id,
                }
            )


DATA_SOURCES_POST_MIDDLEWARE_PARAMETERS = MiddlewareParameters(
    entry_name="Data source",
    relation=RELATION,
    db_client_method=DatabaseClient.add_new_data_source,
)


class DataSourcesPostRequestInfo(PutPostRequestInfo):
    dto: DataSourcesPostDTO


class DataSourcesPutRequestInfo(PutPostRequestInfo):
    dto: DataSourcesPutDTO


class DataSourcesPostHandler(PostHandler):

    def __init__(self):
        super().__init__(middleware_parameters=DATA_SOURCES_POST_MIDDLEWARE_PARAMETERS)

    def pre_execute(self, request: DataSourcesPostRequestInfo):
        request.entry = dataclass_to_filtered_dict(request.dto.entry_data)
        optionally_swap_record_type_name_with_id(
            db_client=self.mp.db_client, entry_data=request.entry
        )

    def post_execute(self, request: DataSourcesPostRequestInfo):
        if request.dto.linked_agency_ids is None:
            return
        for agency_id in request.dto.linked_agency_ids:
            self.mp.db_client.create_data_source_agency_relation(
                column_value_mappings={
                    "data_source_id": request.entry_id,
                    "agency_id": agency_id,
                }
            )


DATA_SOURCES_PUT_MIDDLEWARE_PARAMETERS = MiddlewareParameters(
    entry_name="Data source",
    relation=RELATION,
    db_client_method=DatabaseClient.update_data_source,
)


class DataSourcesPutHandler(PutHandler):

    def __init__(self):
        super().__init__(middleware_parameters=DATA_SOURCES_PUT_MIDDLEWARE_PARAMETERS)

    def pre_execute(self, request: DataSourcesPutRequestInfo):
        request.entry = dataclass_to_filtered_dict(request.dto.entry_data)
        optionally_swap_record_type_name_with_id(
            db_client=self.mp.db_client, entry_data=request.entry
        )


def add_new_data_source_wrapper(
    db_client: DatabaseClient, dto: DataSourcesPostDTO, access_info: AccessInfoPrimary
) -> Response:
    return post_entry_with_handler(
        handler=DataSourcesPostHandler(),
        dto=dto,
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

    return FlaskResponseManager.make_response(
        data={
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
