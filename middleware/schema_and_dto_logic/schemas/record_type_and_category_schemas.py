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


class RecordTypeAndCategoryResponseSchema(Schema):
    record_types = fields.List(
        cls_or_instance=fields.Nested(
            RecordTypeSchema(),
            required=True,
            metadata=get_json_metadata("The list of record types"),
        ),
        metadata=get_json_metadata("The list of record types"),
    )
    record_categories = fields.List(
        cls_or_instance=fields.Nested(
            RecordCategorySchema(),
            required=True,
            metadata=get_json_metadata("The list of record categories"),
        ),
        metadata=get_json_metadata("The list of record categories"),
    )
