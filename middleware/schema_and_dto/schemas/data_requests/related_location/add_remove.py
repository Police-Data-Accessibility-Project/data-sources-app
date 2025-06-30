from middleware.schema_and_dto.dtos.data_requests.by_id.locations import (
    RelatedLocationsByIDDTO,
)
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)

DataRequestsRelatedLocationAddRemoveSchema = pydantic_to_marshmallow(
    RelatedLocationsByIDDTO
)
