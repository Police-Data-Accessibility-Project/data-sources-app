from middleware.schema_and_dto.dtos.search.national import (
    SearchFollowNationalRequestDTO,
)
from middleware.schema_and_dto.dynamic_logic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)

SearchFollowNationalRequestSchema = generate_marshmallow_schema(
    SearchFollowNationalRequestDTO
)
