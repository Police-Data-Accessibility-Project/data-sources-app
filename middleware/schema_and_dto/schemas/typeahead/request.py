from middleware.schema_and_dto.dtos.typeahead import TypeaheadDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)

TypeaheadQuerySchema = pydantic_to_marshmallow(TypeaheadDTO)
