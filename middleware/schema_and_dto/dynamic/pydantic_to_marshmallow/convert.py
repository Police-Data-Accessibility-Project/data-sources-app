from typing import Any, get_origin

from annotated_types import MinLen, MaxLen
from marshmallow import validate
from marshmallow.validate import Validator
from pydantic.fields import FieldInfo

from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.generator.models.field import (
    MarshmallowFieldInfo,
)

from marshmallow.fields import Enum as MarshmallowEnum, Field

from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.mapping import (
    TYPE_MAPPING,
)


def convert_validators(model_field: FieldInfo) -> Validator | None:
    if model_field.annotation is not str:
        return None
    metadata = model_field.metadata
    if len(metadata) == 0:
        return None
    validation_kwargs: dict[str, int] = {}
    for metadata_item in metadata:
        if isinstance(metadata_item, MinLen):
            validation_kwargs["min"] = metadata_item.min_length
        if isinstance(metadata_item, MaxLen):
            validation_kwargs["max"] = metadata_item.max_length
    return validate.Length(**validation_kwargs)


def convert_enum(inner_type: Any) -> MarshmallowFieldInfo:
    return MarshmallowFieldInfo(
        field=MarshmallowEnum,
        field_kwargs={"enum": inner_type, "by_value": True},
    )


def convert_to_marshmallow_class(inner_type: Any) -> type[Field]:
    if get_origin(inner_type) is dict:
        inner_type = dict
    marshmallow_field_cls = TYPE_MAPPING.get(inner_type)
    if marshmallow_field_cls is None:
        raise ValueError(f"Unsupported field type: {inner_type}")
    return marshmallow_field_cls
