from endpoints.instantiations.source_collector.data_sources.sync.dtos.request import (
    SourceCollectorSyncDataSourcesRequestDTO,
)
from endpoints.instantiations.source_collector.data_sources.sync.schema_config import (
    SourceCollectorSyncDataSourceSchemaConfig,
)
from tests.helpers.helper_classes.RequestValidator import RequestValidator


def request_get_data_sources_for_sync(
    rv: RequestValidator, headers: dict, dto: SourceCollectorSyncDataSourcesRequestDTO
):
    return rv.get(
        endpoint="/api/source-collector/data-sources/sync",
        headers=headers,
        query_parameters=dto.model_dump(mode="json"),
        expected_schema=SourceCollectorSyncDataSourceSchemaConfig.primary_output_schema,
    )
