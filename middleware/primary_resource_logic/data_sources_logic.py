from dataclasses import dataclass
from http import HTTPStatus

from flask import make_response, Response

from database_client.database_client import DatabaseClient
from database_client.db_client_dataclasses import OrderByParameters, WhereMapping
from database_client.subquery_logic import SubqueryParameters, SubqueryParameterManager
from database_client.enums import ApprovalStatus
from database_client.result_formatter import ResultFormatter
from middleware.access_logic import AccessInfo
from middleware.dynamic_request_logic.delete_logic import delete_entry
from middleware.dynamic_request_logic.get_by_id_logic import get_by_id
from middleware.dynamic_request_logic.get_many_logic import get_many
from middleware.dynamic_request_logic.post_logic import post_entry
from middleware.dynamic_request_logic.put_logic import put_entry
from middleware.dynamic_request_logic.supporting_classes import (
    MiddlewareParameters,
    IDInfo,
)

from middleware.enums import Relations
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    GetManyBaseDTO,
    EntryCreateUpdateRequestDTO,
    GetByIDBaseDTO,
)
from middleware.common_response_formatting import format_list_response
from middleware.schema_and_dto_logic.primary_resource_schemas.data_sources_schemas import (
    DataSourceEntryDataPostDTO,
)
from middleware.util import dataclass_to_filtered_dict

RELATION = Relations.DATA_SOURCES.value
SUBQUERY_PARAMS = [
    SubqueryParameterManager.agencies()
    # SubqueryParameters(relation_name=Relations.AGENCIES_EXPANDED.value, linking_column="agencies")
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
        format_list_response(zipped_results),
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
    return put_entry(
        middleware_parameters=MiddlewareParameters(
            db_client=db_client,
            entry_name="Data source",
            relation=RELATION,
            db_client_method=DatabaseClient.update_data_source,
            access_info=access_info,
        ),
        entry=dto.entry_data,
        entry_id=data_source_id,
    )


def add_new_data_source_wrapper(
    db_client: DatabaseClient, dto: DataSourceEntryDataPostDTO, access_info: AccessInfo
) -> Response:
    return post_entry(
        middleware_parameters=MiddlewareParameters(
            db_client=db_client,
            access_info=access_info,
            entry_name="Data source",
            relation=RELATION,
            db_client_method=DatabaseClient.add_new_data_source,
        ),
        entry=dataclass_to_filtered_dict(dto.entry_data),
    )
