from enum import Enum
from typing import cast, get_origin, get_args, Any

from marshmallow import Schema
from marshmallow.fields import (
    Field,
    List as MarshmallowList,
    Enum as MarshmallowEnum,
    Nested,
)
from pydantic import BaseModel
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefinedType

from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.generator.helpers import (
    is_optional,
    extract_inner_type,
)
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.generator.models.field import (
    MarshmallowFieldInfo,
)
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.generator.models.metadata import (
    MetadataInfo,
)
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.mapping import (
    TYPE_MAPPING,
)


class MarshmallowSchemaGenerator:

    def __init__(
        self,
        pydantic_model_cls: type[BaseModel],
    ):
        self.pydantic_model_cls = pydantic_model_cls

    @staticmethod
    def process_field(model_field: FieldInfo):
        processor = FieldProcessor(model_field)
        try:
            return processor.process_field()
        except Exception as e:
            raise Exception(f"Error processing field {model_field}: {e}")

    def generate_marshmallow_schema(self) -> type[Schema]:
        schema_fields = {}

        for field_name, model_field in self.pydantic_model_cls.model_fields.items():
            marshmallow_field = self.process_field(model_field)
            schema_fields[field_name] = marshmallow_field

        return type(
            f"{self.pydantic_model_cls.__name__}AutoSchema", (Schema,), schema_fields
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
        metadata_ = {"source": self.metadata_info.source}
        if self.model_field.description:
            metadata_["description"] = self.model_field.description
        return metadata_

    def get_marshmallow_field_cls(self, field_type: type) -> MarshmallowFieldInfo:
        inner_type = extract_inner_type(field_type)
        if get_origin(inner_type) is list:
            return self.get_list_field(inner_type)
        if issubclass(inner_type, Enum):
            return self.get_enum_field(inner_type)
        if issubclass(inner_type, BaseModel):
            return self.get_nested_field(inner_type)

        marshmallow_field_cls = self.get_marshmallow_class(inner_type)
        return MarshmallowFieldInfo(field=marshmallow_field_cls)

    @staticmethod
    def get_marshmallow_class(inner_type: Any) -> type[Field]:
        marshmallow_field_cls = TYPE_MAPPING.get(inner_type)
        if marshmallow_field_cls is None:
            raise ValueError(f"Unsupported field type: {inner_type}")
        return marshmallow_field_cls

    def get_list_field(self, inner_type: list[Any]) -> MarshmallowFieldInfo:
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

    @staticmethod
    def get_nested_field(inner_type: Any) -> MarshmallowFieldInfo:
        schema_generator = MarshmallowSchemaGenerator(inner_type)
        inner_schema = schema_generator.generate_marshmallow_schema()
        return MarshmallowFieldInfo(
            field=Nested,
            field_kwargs={
                "nested": inner_schema(),
            },
        )

    @staticmethod
    def get_enum_field(inner_type: Any) -> MarshmallowFieldInfo:
        return MarshmallowFieldInfo(
            field=MarshmallowEnum,
            field_kwargs={"enum": inner_type, "by_value": True},
        )
