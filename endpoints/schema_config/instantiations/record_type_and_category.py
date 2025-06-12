from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.schemas.record_type_and_category.response import (
    RecordTypeAndCategoryResponseSchema,
)

RecordTypeAndCategoryGetEndpointSchemaConfig = EndpointSchemaConfig(
    primary_output_schema=RecordTypeAndCategoryResponseSchema(),
)
