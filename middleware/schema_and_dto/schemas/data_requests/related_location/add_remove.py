from middleware.schema_and_dto.dtos.data_requests.by_id.locations import (
    RelatedLocationsByIDDTO,
)
from middleware.schema_and_dto.dynamic_logic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)

DataRequestsRelatedLocationAddRemoveSchema = generate_marshmallow_schema(
    RelatedLocationsByIDDTO
)
