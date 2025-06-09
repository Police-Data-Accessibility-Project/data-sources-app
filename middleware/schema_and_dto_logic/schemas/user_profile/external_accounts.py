from marshmallow import Schema, fields

from middleware.schema_and_dto_logic.util import get_json_metadata


class ExternalAccountsSchema(Schema):
    github = fields.Str(
        required=True,
        metadata=get_json_metadata("The GitHub user id of the user"),
    )
