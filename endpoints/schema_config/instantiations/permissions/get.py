from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.primary_resource_logic.permissions import PermissionsGetRequestSchema

PermissionsGetEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=PermissionsGetRequestSchema()
)
