from middleware.schema_and_dto.dtos.data_requests.by_id.source import (
    RelatedSourceByIDDTO,
)
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)

RelatedSourceByIDSchema = generate_marshmallow_schema(RelatedSourceByIDDTO)
