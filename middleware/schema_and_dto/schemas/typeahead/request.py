from middleware.schema_and_dto.dtos.typeahead import TypeaheadDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)

TypeaheadQuerySchema = generate_marshmallow_schema(TypeaheadDTO)
