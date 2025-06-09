from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.dtos.contact import ContactFormPostDTO
from middleware.schema_and_dto.schemas.common.common_response_schemas import (
    MessageSchema,
)
from middleware.schema_and_dto.schemas.contact import ContactFormPostSchema

ContactFormSubmitEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=ContactFormPostSchema(),
    input_dto_class=ContactFormPostDTO,
    primary_output_schema=MessageSchema(),
)
