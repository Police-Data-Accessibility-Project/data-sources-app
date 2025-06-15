from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.dtos.common.base import GetByIDBaseDTO
from middleware.schema_and_dto.schemas.common.base import GetByIDBaseSchema
from middleware.schema_and_dto.schemas.common.common_response_schemas import (
    MessageSchema,
)

AdminUsersByIDDeleteEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=GetByIDBaseSchema(),
    input_dto_class=GetByIDBaseDTO,
    primary_output_schema=MessageSchema(),
)
