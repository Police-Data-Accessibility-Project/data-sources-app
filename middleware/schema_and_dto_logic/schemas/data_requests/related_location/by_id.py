from middleware.schema_and_dto_logic.dtos.data_requests_dtos import RelatedSourceByIDDTO
from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)

RelatedSourceByIDSchema = generate_marshmallow_schema(RelatedSourceByIDDTO)
