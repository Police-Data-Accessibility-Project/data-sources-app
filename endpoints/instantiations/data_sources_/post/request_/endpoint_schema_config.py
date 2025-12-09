from endpoints.instantiations.data_sources_.post.request_.model import (
    PostDataSourceOuterRequest,
)
from endpoints.instantiations.data_sources_.post.request_.schema import (
    PostDataSourceRequestSchema,
)
from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.schemas.common.common_response_schemas import (
    IDAndMessageSchema,
)

PostDataSourceRequestEndpointSchemaConfig = EndpointSchemaConfig(
    primary_output_schema=IDAndMessageSchema(),
    input_schema=PostDataSourceRequestSchema(),
    input_dto_class=PostDataSourceOuterRequest,
)
