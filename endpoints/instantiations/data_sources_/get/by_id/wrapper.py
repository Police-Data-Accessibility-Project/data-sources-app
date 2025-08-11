from flask import Response, make_response

from db.client.core import DatabaseClient
from middleware.primary_resource_logic.data_sources import (
    DataSourcesColumnRequestObject,
    get_data_sources_columns,
)
from middleware.schema_and_dto.dtos.common.base import GetByIDBaseDTO
from middleware.security.access_info.primary import AccessInfoPrimary
from werkzeug.exceptions import NotFound


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
    if result is None:
        raise NotFound("Data Source not found.")

    return make_response(
        {
            "data": result,
            "message": "Successfully retrieved data source",
        }
    )
