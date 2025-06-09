from marshmallow import Schema, fields, validate

from middleware.schema_and_dto_logic.util import get_json_metadata


class SourceCollectorDuplicatesPostRequestSchema(Schema):
    urls = fields.List(
        fields.String(
            required=True,
            metadata=get_json_metadata("The URLs of the data sources to check"),
        ),
        required=True,
        metadata=get_json_metadata("The URLs of the data sources to check"),
        validate=validate.Length(min=1, max=100),
    )
