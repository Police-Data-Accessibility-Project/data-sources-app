from typing import Type, Annotated

from marshmallow import Schema, fields
from pydantic import BaseModel

from middleware.schema_and_dto_logic.common_response_schemas import (
    GetManyResponseSchemaBase,
    MessageSchema,
)
from middleware.schema_and_dto_logic.enums import CSVColumnCondition
from middleware.schema_and_dto_logic.util import get_json_metadata
from utilities.enums import SourceMappingEnum


class SchemaMetadata(BaseModel):
    description: Annotated[
        str, "The description of the field to be displayed in the API docs"
    ]
    source: Annotated[
        SourceMappingEnum,
        "The source of the field when dynamically populated from requests",
    ]
    csv_column_name: Annotated[
        str | CSVColumnCondition | None,
        (
            "The name of the field when represented as a column in a CSV file."
            "Also exists as a flag to indicate that this field should be included "
            "in a CSV representation of the data"
        ),
    ] = None


def create_get_many_schema(
    data_list_schema: type(Schema), description: str
) -> Type[Schema]:
    class GetManySchema(GetManyResponseSchemaBase):
        data = fields.List(
            fields.Nested(
                data_list_schema,
                metadata=get_json_metadata(description),
            ),
            metadata=get_json_metadata(description),
        )

    GetManySchema.__name__ = f"GetMany{data_list_schema.__name__}"

    return GetManySchema


def create_get_by_id_schema(data_schema: Schema, description: str) -> Type[Schema]:
    class GetByIDSchema(MessageSchema):
        data = fields.Nested(
            data_schema,
            metadata=get_json_metadata(description),
        )

    return GetByIDSchema
