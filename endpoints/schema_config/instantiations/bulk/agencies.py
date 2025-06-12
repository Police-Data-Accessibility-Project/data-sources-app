from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.dtos.agencies.post import AgenciesPostDTO
from middleware.schema_and_dto.schemas.bulk.agencies import (
    AgenciesPostBatchRequestSchema,
)
from middleware.schema_and_dto.schemas.bulk.response import BatchPostResponseSchema

BulkAgenciesPostEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=AgenciesPostBatchRequestSchema(),
    input_dto_class=AgenciesPostDTO,
    primary_output_schema=BatchPostResponseSchema(),
)
