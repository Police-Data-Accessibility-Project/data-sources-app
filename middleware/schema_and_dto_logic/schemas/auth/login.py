from marshmallow import fields

from middleware.schema_and_dto_logic.schemas.common.common_response_schemas import (
    MessageSchema,
)
from middleware.schema_and_dto_logic.util import get_json_metadata


class LoginResponseSchema(MessageSchema):
    access_token = fields.Str(
        metadata=get_json_metadata("The access token for the user's PDAP account"),
    )
    refresh_token = fields.Str(
        metadata=get_json_metadata("The refresh token for the user's PDAP account"),
    )
