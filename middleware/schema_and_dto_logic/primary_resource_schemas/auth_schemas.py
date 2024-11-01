from marshmallow import Schema, fields

from middleware.schema_and_dto_logic.common_response_schemas import MessageSchema
from middleware.schema_and_dto_logic.util import get_json_metadata, get_query_metadata


class LoginResponseSchema(MessageSchema):
    access_token = fields.Str(
        metadata=get_json_metadata("The access token for the user's PDAP account"),
    )
    refresh_token = fields.Str(
        metadata=get_json_metadata("The refresh token for the user's PDAP account"),
    )

class LinkToGithubRequestSchema(Schema):
    user_email = fields.Str(
        metadata=get_json_metadata("The email address of the user"),
    )
    redirect_to = fields.Str(
        metadata=get_json_metadata("The URL to redirect the user to after linking to Github"),
    )