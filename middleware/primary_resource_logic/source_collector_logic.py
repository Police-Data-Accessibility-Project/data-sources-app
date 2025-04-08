from database_client.database_client import DatabaseClient
from middleware.common_response_formatting import message_response
from middleware.flask_response_manager import FlaskResponseManager
from middleware.schema_and_dto_logic.primary_resource_dtos.source_collector_dtos import (
    SourceCollectorPostRequestDTO,
)


def add_data_sources_from_source_collector(
    db_client: DatabaseClient, dto: SourceCollectorPostRequestDTO
):
    results = db_client.add_data_sources_from_source_collector(dto.data_sources)

    return FlaskResponseManager.make_response(
        data={
            "message": "Successfully processed data sources",
            "data_sources": [result.model_dump(mode="json") for result in results],
        }
    )
