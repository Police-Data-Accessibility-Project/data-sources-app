from dataclasses import dataclass
from http import HTTPStatus
from typing import List, Optional

from flask import make_response, Response

from database_client.database_client import DatabaseClient
from database_client.db_client_dataclasses import OrderByParameters, WhereMapping
from database_client.subquery_logic import SubqueryParameters, SubqueryParameterManager
from database_client.enums import ApprovalStatus
from database_client.result_formatter import ResultFormatter
from middleware.access_logic import AccessInfo
from middleware.column_permission_logic import RelationRoleParameters
from middleware.custom_dataclasses import DeferredFunction
from middleware.dynamic_request_logic.delete_logic import delete_entry
from middleware.dynamic_request_logic.get_by_id_logic import get_by_id
from middleware.dynamic_request_logic.get_many_logic import get_many
from middleware.dynamic_request_logic.get_related_resource_logic import (
    GetRelatedResourcesParameters,
    get_related_resource,
)
from middleware.dynamic_request_logic.post_logic import post_entry, PostLogic
from middleware.dynamic_request_logic.put_logic import put_entry
from middleware.dynamic_request_logic.supporting_classes import (
    MiddlewareParameters,
    IDInfo,
)

from middleware.enums import Relations
from middleware.primary_resource_logic.data_requests import RelatedSourceByIDDTO
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    GetManyBaseDTO,
    EntryCreateUpdateRequestDTO,
    GetByIDBaseDTO,
)
from middleware.common_response_formatting import format_list_response, message_response
from middleware.schema_and_dto_logic.primary_resource_schemas.data_sources_schemas import (
    DataSourceEntryDataPostDTO, DataSourcesPostDTO,
)
from middleware.util import dataclass_to_filtered_dict

RELATION = Relations.DATA_SOURCES.value
SUBQUERY_PARAMS = [
    SubqueryParameterManager.agencies()
]


class DataSourceNotFoundError(Exception):
    pass


@dataclass
class DataSourcesGetManyRequestDTO(GetManyBaseDTO):
    approval_status: ApprovalStatus = ApprovalStatus.APPROVED
    page_number: int = 1


def get_data_sources_wrapper(
    db_client: DatabaseClient,
    access_info: AccessInfo,
    dto: DataSourcesGetManyRequestDTO,
) -> Response:
    return get_many(
        middleware_parameters=MiddlewareParameters(
            access_info=access_info,
            relation=Relations.DATA_SOURCES_EXPANDED.value,
            db_client_method=DatabaseClient.get_data_sources,
            db_client=db_client,
            db_client_additional_args={
                "order_by": OrderByParameters.construct_from_args(
                    sort_by=dto.sort_by,
                    sort_order=dto.sort_order,
                ),
                "where_mappings": [
                    WhereMapping(
                        column="approval_status", value=dto.approval_status.value
                    )
                ],
                "build_metadata": True,
            },
            entry_name="data source",
            subquery_parameters=SUBQUERY_PARAMS,
        ),
        page=dto.page,
        requested_columns=dto.requested_columns,
    )


def data_source_by_id_wrapper(
    db_client: DatabaseClient, access_info: AccessInfo, dto: GetByIDBaseDTO
) -> Response:
    return get_by_id(
        middleware_parameters=MiddlewareParameters(
            access_info=access_info,
            relation=Relations.DATA_SOURCES_EXPANDED.value,
            db_client_method=DatabaseClient.get_data_sources,
            db_client=db_client,
            entry_name="data source",
            subquery_parameters=SUBQUERY_PARAMS,
        ),
        id=dto.resource_id,
        id_column_name="id",
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
    access_info: AccessInfo,
    data_source_id: str,
) -> Response:
    return delete_entry(
        middleware_parameters=MiddlewareParameters(
            access_info=access_info,
            relation=RELATION,
            db_client_method=DatabaseClient.delete_data_source,
            db_client=db_client,
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
    access_info: AccessInfo,
    data_source_id: str,
) -> Response:
    entry_data = dto.entry_data
    optionally_swap_record_type_name_with_id(db_client, entry_data)
    return put_entry(
        middleware_parameters=MiddlewareParameters(
            db_client=db_client,
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
                column_value_mappings = {
                    "data_source_id": self.id_val,
                    "agency_id": agency_id
                }
            )



def add_new_data_source_wrapper(
    db_client: DatabaseClient, dto: DataSourcesPostDTO, access_info: AccessInfo
) -> Response:
    entry_data = dataclass_to_filtered_dict(dto.entry_data)
    optionally_swap_record_type_name_with_id(db_client, entry_data)
    post_logic = DataSourcesPostLogic(
        middleware_parameters=MiddlewareParameters(
            db_client=db_client,
            access_info=access_info,
            entry_name="Data source",
            relation=RELATION,
            db_client_method=DatabaseClient.add_new_data_source,
        ),
        entry=entry_data,
        agency_ids=dto.linked_agency_ids,
    )
    return post_logic.execute()
# region Related Resources


def get_data_source_related_agencies(
    db_client: DatabaseClient, dto: GetByIDBaseDTO
) -> Response:
    return get_related_resource(
        get_related_resources_parameters=GetRelatedResourcesParameters(
            db_client=db_client,
            dto=dto,
            db_client_method=DatabaseClient.get_data_sources,
            primary_relation=Relations.DATA_SOURCES,
            related_relation=Relations.AGENCIES_EXPANDED,
            linking_column="agencies",
            metadata_count_name="agencies_count",
            resource_name="agencies",
        )
    )


class CreateDataSourceRelatedAgenciesLogic(PostLogic):

    def make_response(self) -> Response:
        return message_response("Agency successfully associated with data source.")


def create_data_source_related_agency(
    db_client: DatabaseClient,
    access_info: AccessInfo,
    dto: RelatedSourceByIDDTO,
) -> Response:
    post_logic = CreateDataSourceRelatedAgenciesLogic(
        middleware_parameters=MiddlewareParameters(
            db_client=db_client,
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
    access_info: AccessInfo,
    dto: RelatedSourceByIDDTO,
) -> Response:
    return delete_entry(
        middleware_parameters=MiddlewareParameters(
            db_client=db_client,
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
