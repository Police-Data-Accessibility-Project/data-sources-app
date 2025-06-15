from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.primary_resource_logic.data_sources import DataSourcesGetManyRequestDTO
from middleware.schema_and_dto.dtos.common.base import GetManyBaseDTO
from middleware.schema_and_dto.schemas.data_sources.get.many.request import (
    DataSourcesGetManyRequestSchema,
)
from middleware.schema_and_dto.schemas.data_sources.get.many.response import (
    DataSourcesGetManySchema,
)

DataSourcesGetManyEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=DataSourcesGetManyRequestSchema(),
    primary_output_schema=DataSourcesGetManySchema(),
    input_dto_class=DataSourcesGetManyRequestDTO,
)
