from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.dtos.archives import ArchivesGetRequestDTO
from middleware.schema_and_dto.schemas.archives.get.request import (
    ArchivesGetRequestSchema,
)
from middleware.schema_and_dto.schemas.archives.get.response import (
    ArchivesGetResponseSchema,
)

ArchivesGetEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=ArchivesGetRequestSchema(),
    input_dto_class=ArchivesGetRequestDTO,
    primary_output_schema=ArchivesGetResponseSchema(many=True),
)
