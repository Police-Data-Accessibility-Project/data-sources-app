from typing import Type

from marshmallow import Schema, fields

from middleware.schema_and_dto_logic.common_response_schemas import (
    GetManyResponseSchemaBase,
    MessageSchema,
)
from middleware.schema_and_dto_logic.util import get_json_metadata


def create_get_many_schema(data_list_schema: Schema, description: str) -> Type[Schema]:
    class GetManySchema(GetManyResponseSchemaBase):
        data = fields.List(
            fields.Nested(
                data_list_schema,
                metadata=get_json_metadata(description),
            ),
            metadata=get_json_metadata(description),
        )

    GetManySchema.__name__ = f"GetMany{data_list_schema.__class__.__name__}"

    return GetManySchema


def create_get_by_id_schema(data_schema: Schema, description: str) -> Type[Schema]:
    class GetByIDSchema(MessageSchema):
        data = fields.Nested(
            data_schema,
            metadata=get_json_metadata(description),
        )

    return GetByIDSchema
