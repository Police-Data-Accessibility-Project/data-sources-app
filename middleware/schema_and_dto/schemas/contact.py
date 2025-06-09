from marshmallow import Schema, fields

from middleware.enums import ContactFormMessageType
from middleware.schema_and_dto.dynamic_logic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)
from middleware.schema_and_dto.dtos.contact import (
    ContactFormPostDTO,
)
from middleware.schema_and_dto.util import get_json_metadata

ContactFormPostSchema = generate_marshmallow_schema(ContactFormPostDTO)
