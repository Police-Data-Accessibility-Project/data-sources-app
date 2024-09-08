from dataclasses import dataclass
from http import HTTPStatus

from flask import make_response, Response
from marshmallow import fields, validate

from database_client.database_client import DatabaseClient
from database_client.db_client_dataclasses import OrderByParameters
from database_client.enums import ApprovalStatus
from database_client.result_formatter import ResultFormatter
from middleware.access_logic import AccessInfo
from middleware.dynamic_request_logic import (
    post_entry,
    MiddlewareParameters,
    get_by_id,
    put_entry,
    get_many,
    delete_entry,
)
from middleware.enums import Relations
from middleware.schema_and_dto_logic.common_schemas_and_dtos import GetBaseSchema, GetManyBaseDTO, EntryDataRequestDTO
from middleware.common_response_formatting import format_list_response
from utilities.enums import SourceMappingEnum

RELATION = Relations.DATA_SOURCES.value


class DataSourceNotFoundError(Exception):
    pass


class DataSourcesGetRequestSchema(GetBaseSchema):
    approval_status = fields.Str(
        required=False,
        description="Approval status of returned data sources.",
        source=SourceMappingEnum.QUERY_ARGS,
        validate=validate.OneOf([e.value for e in ApprovalStatus]),
        default="approved",
    )


@dataclass
class DataSourcesGetRequestDTOMany(GetManyBaseDTO):
    approval_status: ApprovalStatus = ApprovalStatus.APPROVED


def get_data_sources_wrapper(
    db_client: DatabaseClient,
    access_info: AccessInfo,
    dto: DataSourcesGetRequestDTOMany,
) -> Response:
    return get_many(
        middleware_parameters=MiddlewareParameters(
            access_info=access_info,
            relation=RELATION,
            db_client_method=DatabaseClient.get_data_sources,
            db_client=db_client,
            db_client_additional_args={
                "order_by": OrderByParameters.construct_from_args(
                    sort_by=dto.sort_by,
                    sort_order=dto.sort_order,
                ),
                "where_mappings": {"approval_status": dto.approval_status.value},
            },
            entry_name="data source",
        ),
        page=dto.page,
    )


def data_source_by_id_wrapper(
    db_client: DatabaseClient, access_info: AccessInfo, data_source_id: int
) -> Response:
    return get_by_id(
        middleware_parameters=MiddlewareParameters(
            access_info=access_info,
            relation=RELATION,
            db_client_method=DatabaseClient.get_data_sources,
            db_client=db_client,
            entry_name="data source",
        ),
        id=data_source_id,
        id_column_name="airtable_uid",
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
        entry_id=data_source_id,
        id_column_name="airtable_uid",
    )


def update_data_source_wrapper(
    db_client: DatabaseClient,
    dto: EntryDataRequestDTO,
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
    db_client: DatabaseClient, dto: EntryDataRequestDTO, access_info: AccessInfo
) -> Response:
    return post_entry(
        middleware_parameters=MiddlewareParameters(
            db_client=db_client,
            access_info=access_info,
            entry_name="Data source",
            relation=RELATION,
            db_client_method=DatabaseClient.add_new_data_source,
        ),
        entry=dto.entry_data,
    )
