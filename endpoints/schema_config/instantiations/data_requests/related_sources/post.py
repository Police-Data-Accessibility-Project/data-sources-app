from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.dtos.data_requests.by_id.source import (
    RelatedSourceByIDDTO,
)
from middleware.schema_and_dto.schemas.data_requests.related_location.by_id import (
    RelatedSourceByIDSchema,
)

DataRequestsRelatedSourcesPost = EndpointSchemaConfig(
    input_schema=RelatedSourceByIDSchema(), input_dto_class=RelatedSourceByIDDTO
)
