from flask_restx import fields as restx_fields
from marshmallow import fields as marshmallow_fields

from middleware.schema_and_dto_logic.custom_fields import (
    DataField,
    EntryDataListField,
)
from middleware.schema_and_dto_logic.enums import RestxModelPlaceholder

MARSHMALLOW_TO_RESTX_FIELD_MAPPING = {
    marshmallow_fields.Str: restx_fields.String,
    marshmallow_fields.Int: restx_fields.Integer,
    marshmallow_fields.Bool: restx_fields.Boolean,
    marshmallow_fields.Email: restx_fields.String,  # Email can map to a String field in flask_restx
    marshmallow_fields.List: restx_fields.List,
    marshmallow_fields.Nested: restx_fields.Nested,
    marshmallow_fields.URL: restx_fields.Url,
    marshmallow_fields.Enum: restx_fields.String,
    marshmallow_fields.Float: restx_fields.Float,
    marshmallow_fields.DateTime: restx_fields.DateTime,
    marshmallow_fields.Date: restx_fields.Date,
    marshmallow_fields.Dict: restx_fields.Raw,
    DataField: RestxModelPlaceholder.VARIABLE_COLUMNS,
    EntryDataListField: RestxModelPlaceholder.LIST_VARIABLE_COLUMNS,
    # Add more mappings as needed
}
RESTX_FIELD_TO_NATIVE_TYPE_MAPPING = {
    restx_fields.String: str,
    restx_fields.Integer: int,
    restx_fields.Boolean: bool,
    restx_fields.List: list,
    restx_fields.Nested: dict,
    restx_fields.Url: str,
    restx_fields.DateTime: str,
}
