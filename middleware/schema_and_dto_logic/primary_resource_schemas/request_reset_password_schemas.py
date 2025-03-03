from marshmallow import Schema, fields

from middleware.schema_and_dto_logic.util import get_json_metadata


class RequestResetPasswordRequestSchema(Schema):
    email = fields.String(
        required=True,
        metadata=get_json_metadata("The email address associated with the account."),
    )
