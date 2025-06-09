from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.dtos.data_sources.post import DataSourcesPostDTO
from middleware.schema_and_dto.schemas.bulk.data_sources import (
    DataSourcesPostBatchRequestSchema,
)
from middleware.schema_and_dto.schemas.bulk.response import BatchPostResponseSchema

BulkDataSourcesPostEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=DataSourcesPostBatchRequestSchema(),
    input_dto_class=DataSourcesPostDTO,
    primary_output_schema=BatchPostResponseSchema(),
)
