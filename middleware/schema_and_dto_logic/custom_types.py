from typing import Union, TypeVar

from flask_restx import fields as restx_fields
from marshmallow import fields as marshmallow_fields, Schema

from middleware.schema_and_dto_logic.custom_fields import DataField
from middleware.schema_and_dto_logic.enums import RestxModelPlaceholder

MarshmallowFields = Union[
    marshmallow_fields.Str,
    marshmallow_fields.Int,
    marshmallow_fields.Bool,
    marshmallow_fields.Email,
    marshmallow_fields.List,
    DataField,
]
RestxFields = Union[
    restx_fields.String,
    restx_fields.Integer,
    restx_fields.Boolean,
    restx_fields.List,
    restx_fields.Nested,
    RestxModelPlaceholder,
]
DTOTypes = TypeVar("DTOTypes")
SchemaTypes = TypeVar("SchemaTypes", bound=Schema)
ValidationSchema = TypeVar("ValidationSchema", bound=Schema)
