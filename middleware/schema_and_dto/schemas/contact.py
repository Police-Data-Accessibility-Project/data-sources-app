from middleware.schema_and_dto.dtos.contact import (
    ContactFormPostDTO,
)
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)

ContactFormPostSchema = pydantic_to_marshmallow(ContactFormPostDTO)
