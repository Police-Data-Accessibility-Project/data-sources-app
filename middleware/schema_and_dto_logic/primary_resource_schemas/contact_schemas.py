from marshmallow import Schema, fields

from middleware.enums import ContactFormMessageType
from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)
from middleware.schema_and_dto_logic.primary_resource_dtos.contact_dtos import (
    ContactFormPostDTO,
)
from middleware.schema_and_dto_logic.util import get_json_metadata

ContactFormPostSchema = generate_marshmallow_schema(ContactFormPostDTO)
