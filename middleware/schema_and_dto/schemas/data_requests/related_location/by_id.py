from middleware.schema_and_dto.dtos.data_requests.by_id.source import (
    RelatedSourceByIDDTO,
)
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)

RelatedSourceByIDSchema = pydantic_to_marshmallow(RelatedSourceByIDDTO)
