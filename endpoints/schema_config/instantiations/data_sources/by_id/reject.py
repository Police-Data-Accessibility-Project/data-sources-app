from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.dtos.data_sources.reject import DataSourcesRejectDTO
from middleware.schema_and_dto.schemas.common.common_response_schemas import (
    MessageSchema,
)
from middleware.schema_and_dto.schemas.data_sources.reject import DataSourceRejectSchema

DataSourcesByIDRejectEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=DataSourceRejectSchema(),
    input_dto_class=DataSourcesRejectDTO,
    primary_output_schema=MessageSchema(),
)
