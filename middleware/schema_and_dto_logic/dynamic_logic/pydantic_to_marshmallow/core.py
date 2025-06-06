from marshmallow import Schema
from pydantic import BaseModel

from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.helpers import (
    is_optional,
    extract_inner_type,
)
from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.mapping import (
    TYPE_MAPPING,
)
from utilities.enums import SourceMappingEnum


def generate_marshmallow_schema(pydantic_model_cls: type[BaseModel]) -> type[Schema]:
    schema_fields = {}

    for field_name, model_field in pydantic_model_cls.model_fields.items():
        field_type = model_field.annotation

        allow_none = is_optional(field_type)

        if model_field.json_schema_extra is None:
            model_field.json_schema_extra = {}
        is_required = model_field.json_schema_extra.get("required", True)

        inner_type = extract_inner_type(field_type)
        marshmallow_field_cls = TYPE_MAPPING.get(inner_type)

        if marshmallow_field_cls is None:
            raise ValueError(f"Unsupported field type: {inner_type}")

        # Prepare metadata (handle description)
        metadata = {"source": SourceMappingEnum.JSON}
        if model_field.description:
            metadata["description"] = model_field.description

        # Instantiate the marshmallow field
        marshmallow_field = marshmallow_field_cls(
            required=is_required, allow_none=allow_none, metadata=metadata
        )

        schema_fields[field_name] = marshmallow_field

    return type(f"{pydantic_model_cls.__name__}AutoSchema", (Schema,), schema_fields)
