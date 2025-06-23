from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.primary_resource_logic.permissions import (
    PermissionsPutRequestSchema,
    PermissionsRequestDTO,
)

PermissionsPutEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=PermissionsPutRequestSchema(),
    input_dto_class=PermissionsRequestDTO,
)
