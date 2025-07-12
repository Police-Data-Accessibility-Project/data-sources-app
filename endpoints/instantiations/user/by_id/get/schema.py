from marshmallow import Schema, fields

from endpoints.instantiations.user.by_id.get.dto import ExternalAccountDTO, UserProfileResponseSchemaInnerDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import pydantic_to_marshmallow
from middleware.schema_and_dto.util import get_json_metadata

ExternalAccountsSchema = pydantic_to_marshmallow(ExternalAccountDTO)


UserProfileResponseSchemaInner = pydantic_to_marshmallow(UserProfileResponseSchemaInnerDTO)


class UserProfileResponseSchema(Schema):
    data = fields.Nested(
        UserProfileResponseSchemaInner(),
        metadata=get_json_metadata("The result"),
    )

