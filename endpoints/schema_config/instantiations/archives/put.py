from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.schemas.archives.put import ArchivesPutRequestSchema

ArchivesPutEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=ArchivesPutRequestSchema(),
)
