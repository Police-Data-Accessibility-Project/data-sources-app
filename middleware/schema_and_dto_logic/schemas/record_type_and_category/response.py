from marshmallow import Schema, fields

from middleware.schema_and_dto_logic.schemas.record_type_and_category.record_category import (
    RecordCategorySchema,
)
from middleware.schema_and_dto_logic.schemas.record_type_and_category.record_type import (
    RecordTypeSchema,
)
from middleware.schema_and_dto_logic.util import get_json_metadata


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
