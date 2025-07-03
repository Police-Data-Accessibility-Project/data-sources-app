from enum import Enum

from marshmallow import fields, Schema

from middleware.schema_and_dto.util import get_json_metadata


def enum_field(
    enum_type: type[Enum],
    description: str = None,
    required: bool = True,
    allow_none: bool = False,
) -> fields.Enum:
    return fields.Enum(
        required=required,
        enum=enum_type,
        by_value=fields.Str,
        allow_none=allow_none,
        metadata=get_json_metadata(description),
    )


def int_field(
    description: str = None,
    required: bool = True,
    allow_none: bool = False,
) -> fields.Integer:
    return fields.Integer(
        required=required,
        allow_none=allow_none,
        metadata=get_json_metadata(description),
    )


def str_field(
    description: str = None,
    required: bool = True,
    allow_none: bool = False,
) -> fields.String:
    return fields.String(
        required=required,
        allow_none=allow_none,
        metadata=get_json_metadata(description),
    )


def nested_field(
    nested: Schema | type[Schema],
    required: bool = True,
    allow_none: bool = False,
    description: str = None,
) -> fields.Nested:
    return fields.Nested(
        nested,
        required=required,
        allow_none=allow_none,
        metadata=get_json_metadata(description),
    )


def date_field(
    description: str = None,
    required: bool = True,
    allow_none: bool = False,
) -> fields.Date:
    return fields.Date(
        required=required,
        allow_none=allow_none,
        metadata=get_json_metadata(description),
    )
