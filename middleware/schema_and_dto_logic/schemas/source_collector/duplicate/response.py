from marshmallow import Schema, fields

from middleware.schema_and_dto_logic.util import get_json_metadata


class SourceCollectorDuplicatePostResponseSchema(Schema):
    results = fields.Dict(
        keys=fields.String(
            required=True,
            metadata=get_json_metadata("The URLs of the data sources to check"),
        ),
        values=fields.Boolean(
            required=True,
            metadata=get_json_metadata("The results of the duplicate check"),
        ),
        required=True,
        metadata=get_json_metadata(
            "The results of the duplicate check",
        ),
    )
