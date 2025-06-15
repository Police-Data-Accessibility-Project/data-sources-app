from marshmallow import Schema, fields

from middleware.schema_and_dto.util import get_json_metadata


class RecordCategorySchema(Schema):
    id = fields.Integer(
        required=True, metadata=get_json_metadata("The id of the record category")
    )
    name = fields.String(
        required=True, metadata=get_json_metadata("The name of the record category")
    )
    description = fields.String(
        required=True,
        allow_none=True,
        metadata=get_json_metadata("The description of the record category"),
    )
