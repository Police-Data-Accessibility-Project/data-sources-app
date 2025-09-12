from flask import Response, make_response

from db.client.core import DatabaseClient
from endpoints.instantiations.data_sources_.get.by_id.agencies.query import (
    GetDataSourceRelatedAgenciesQueryBuilder,
)
from middleware.common_response_formatting import message_response
from middleware.schema_and_dto.dtos.common.base import GetByIDBaseDTO


def get_data_source_related_agencies(
    db_client: DatabaseClient, dto: GetByIDBaseDTO
) -> Response:
    results: list[dict] | None = db_client.run_query_builder(
        GetDataSourceRelatedAgenciesQueryBuilder(data_source_id=int(dto.resource_id))
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
