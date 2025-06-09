from enum import Enum
from typing import cast, get_origin, get_args

from marshmallow.fields import Field, Enum as MarshmallowEnum, List as MarshmallowList
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefinedType

from middleware.schema_and_dto.dynamic_logic.pydantic_to_marshmallow.generator.models.field import (
    MarshmallowFieldInfo,
)
from middleware.schema_and_dto.dynamic_logic.pydantic_to_marshmallow.generator.models.metadata import (
    MetadataInfo,
)
from middleware.schema_and_dto.dynamic_logic.pydantic_to_marshmallow.generator.helpers import (
    is_optional,
    extract_inner_type,
)
from middleware.schema_and_dto.dynamic_logic.pydantic_to_marshmallow.mapping import (
    TYPE_MAPPING,
)


class FieldProcessor:

    def __init__(self, model_field: FieldInfo):
        self.model_field = model_field
        if self.model_field.json_schema_extra is None:
            self.model_field.json_schema_extra = {}
        if isinstance(self.model_field.json_schema_extra, dict):
            self.metadata_info: MetadataInfo = MetadataInfo(
                **self.model_field.json_schema_extra
            )
        else:
            self.metadata_info: MetadataInfo = cast(
                MetadataInfo, self.model_field.json_schema_extra
            )
        self.field_type = self.model_field.annotation

    def get_additional_kwargs(self):
        if not isinstance(self.model_field.default, PydanticUndefinedType):
            additional_kwargs = {"load_default": self.model_field.default}
        else:
            additional_kwargs = {}
        return additional_kwargs

    def process_field(self) -> Field:
        allow_none = is_optional(self.field_type)

        additional_kwargs = self.get_additional_kwargs()

        marshmallow_field_info = self.get_marshmallow_field_cls(self.field_type)
        # Combine kwargs
        marshmallow_field_info.field_kwargs = {
            **marshmallow_field_info.field_kwargs,
            **additional_kwargs,
        }

        # Instantiate the marshmallow field
        marshmallow_field = marshmallow_field_info.field(
            required=self.metadata_info.required,
            allow_none=allow_none,
            metadata=self.prepare_metadata(),
            **marshmallow_field_info.field_kwargs,
        )

        return marshmallow_field

    def prepare_metadata(self):
        metadata = {"source": self.metadata_info.source}
        if self.model_field.description:
            metadata["description"] = self.model_field.description
        return metadata

    def get_marshmallow_field_cls(self, field_type: type) -> MarshmallowFieldInfo:
        inner_type = extract_inner_type(field_type)
        # If enum, we need to use EnumField
        if issubclass(inner_type, Enum):
            return MarshmallowFieldInfo(
                field=MarshmallowEnum,
                field_kwargs={"enum": inner_type, "by_value": True},
            )
        if get_origin(inner_type) is list:
            type_arg = get_args(inner_type)[0]

            type_arg_field_info = self.get_marshmallow_field_cls(type_arg)

            type_arg_field_instance = type_arg_field_info.field(
                required=self.metadata_info.required,
                allow_none=is_optional(type_arg),
                metadata=self.prepare_metadata(),
                **type_arg_field_info.field_kwargs,
            )

            return MarshmallowFieldInfo(
                field=MarshmallowList,
                field_kwargs={
                    "cls_or_instance": type_arg_field_instance,
                },
            )

        marshmallow_field_cls = TYPE_MAPPING.get(inner_type)
        if marshmallow_field_cls is None:
            raise ValueError(f"Unsupported field type: {inner_type}")
        return MarshmallowFieldInfo(field=marshmallow_field_cls)
