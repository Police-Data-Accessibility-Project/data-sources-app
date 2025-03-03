from marshmallow import Schema, fields

from middleware.schema_and_dto_logic.util import get_json_metadata


# TODO: Add to test.
class APIKeyResponseSchema(Schema):
    api_key = fields.String(
        required=True,
        metadata=get_json_metadata(
            description="The generated API key.",
        ),
    )
