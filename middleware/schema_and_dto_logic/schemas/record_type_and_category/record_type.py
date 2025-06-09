from marshmallow import Schema, fields

from middleware.schema_and_dto_logic.util import get_json_metadata


class RecordTypeSchema(Schema):
    id = fields.Integer(
        required=True, metadata=get_json_metadata("The id of the record type")
    )
    name = fields.String(
        required=True, metadata=get_json_metadata("The name of the record type")
    )
    description = fields.String(
        required=True, metadata=get_json_metadata("The description of the record type")
    )
    category_id = fields.Integer(
        required=True,
        metadata=get_json_metadata(
            "The id of the record category the record type is a part of"
        ),
    )
