from marshmallow import Schema, fields

from middleware.schema_and_dto_logic.util import get_json_metadata


class ArchivesGetResponseSchema(Schema):
    id = fields.Integer(
        required=True, metadata=get_json_metadata("The ID of the archive")
    )
    last_cached = fields.DateTime(
        required=True,
        metadata=get_json_metadata("The last date the archive was cached"),
    )
    source_url = fields.String(
        required=True, metadata=get_json_metadata("The URL of the archive")
    )
    update_frequency = fields.String(
        required=True, metadata=get_json_metadata("The archive update frequency")
    )
