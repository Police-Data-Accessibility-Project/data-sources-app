from middleware.schema_and_dto.dtos.contact import (
    ContactFormPostDTO,
)
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)

ContactFormPostSchema = generate_marshmallow_schema(ContactFormPostDTO)
