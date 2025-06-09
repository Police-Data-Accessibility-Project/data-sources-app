from marshmallow import Schema, fields

from middleware.schema_and_dto.util import get_json_metadata


class APIKeyResponseSchema(Schema):
    api_key = fields.String(
        required=True,
        metadata=get_json_metadata(
            description="The generated API key.",
        ),
    )
