from dataclasses import dataclass
from typing import Optional

from marshmallow import Schema, fields, validate
from pydantic import BaseModel

from utilities.enums import SourceMappingEnum


class ExampleSchemaWithEnum(Schema):
    example_enum = fields.String(
        required=True,
        source=SourceMappingEnum.QUERY_ARGS,
        description="An example query string.",
        validate=validate.OneOf(["a", "b"]),
    )


class ExampleDTOWithEnum(BaseModel):
    example_enum: str



@dataclass
class ExampleDTO:
    example_string: str
    example_query_string: str

@dataclass
class SimpleDTO:
    simple_string: str
    optional_int: Optional[int] = None
    transformed_array: Optional[list[str]] = None



class ExampleSchema(Schema):
    example_string = fields.String(
        required=True,
        source=SourceMappingEnum.JSON,
        description="An example string",
    )
    example_query_string = fields.String(
        required=True,
        source=SourceMappingEnum.QUERY_ARGS,
        description="An example query string",
    )


class ExampleNestedSchema(Schema):
    example_dto_with_enum = fields.Nested(
        ExampleSchemaWithEnum,
        required=True,
        source=SourceMappingEnum.JSON,
        description="An example description.",
        metadata={
            "nested_dto_class": ExampleDTOWithEnum,
        },
    )
    example_dto = fields.Nested(
        ExampleSchema,
        required=True,
        source=SourceMappingEnum.JSON,
        description="An example description.",
        metadata={"nested_dto_class": ExampleDTO},
    )


class ExampleNestedDTO(BaseModel):
    example_dto_with_enum: ExampleDTOWithEnum
    example_dto: ExampleDTO


class ExampleNestedSchemaWithIncorrectSource(Schema):
    example_dto_with_enum = fields.Nested(
        ExampleSchemaWithEnum,
        required=True,
        source=SourceMappingEnum.QUERY_ARGS,
        description="An example query string.",
    )
    example_dto = fields.Nested(
        ExampleSchema,
        required=True,
        source=SourceMappingEnum.JSON,
        description="An example query string.",
    )




class ExampleSchemaWithoutForm(Schema):
    example_string = fields.String(
        required=True,
        source=SourceMappingEnum.JSON,
        description="An example string",
    )
    example_query_string = fields.String(
        required=True,
        source=SourceMappingEnum.QUERY_ARGS,
        description="An example query string",
    )

SAMPLE_REQUEST_ARGS = {
    "simple_string": "spam",
    "optional_int": None,
    "transformed_array": "hello,world",
}
