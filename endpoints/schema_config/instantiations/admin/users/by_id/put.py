from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.dtos.admin.put import AdminUserPutDTO
from middleware.schema_and_dto.schemas.admin.put import AdminUsersPutSchema
from middleware.schema_and_dto.schemas.common.common_response_schemas import (
    MessageSchema,
)

AdminUsersByIDPutEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=AdminUsersPutSchema(),
    input_dto_class=AdminUserPutDTO,
    primary_output_schema=MessageSchema(),
)
