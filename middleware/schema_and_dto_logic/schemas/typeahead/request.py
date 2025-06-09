from middleware.schema_and_dto_logic.dtos.typeahead import TypeaheadDTO
from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)

TypeaheadQuerySchema = generate_marshmallow_schema(TypeaheadDTO)
