from enum import Enum
from types import GenericAlias
from typing import cast, get_origin, get_args

from marshmallow import Schema
from marshmallow.fields import Field, Enum as MarshmallowEnum
from pydantic import BaseModel
from pydantic.fields import FieldInfo, Field as PydanticField
from pydantic_core import PydanticUndefinedType

from middleware.schema_and_dto.dynamic_logic.pydantic_to_marshmallow.helpers import (
    is_optional,
    extract_inner_type,
)
from middleware.schema_and_dto.dynamic_logic.pydantic_to_marshmallow.mapping import (
    TYPE_MAPPING,
)
from utilities.enums import SourceMappingEnum


class MetadataInfo(BaseModel):
    """
    This hijacks the pydantic field json_schema_extra
    to provide a consistent interface for marshmallow metadata
    """

    source: SourceMappingEnum = SourceMappingEnum.JSON
    required: bool = True

    def get(self, key: str, default=None):
        return self.model_dump().get(key, default)


class MarshmallowFieldInfo(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    field: type[Field]
    field_kwargs: dict = PydanticField(default_factory=dict)


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

        metadata = self.prepare_metadata()

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
            type_arg_field = self.get_marshmallow_field_cls(type_arg)

            return MarshmallowFieldInfo(
                field=Field,
                field_kwargs={
                    "cls_or_instance": type_arg_field.field(
                        metadata=self.prepare_metadata()
                    ),
                },
            )

        marshmallow_field_cls = TYPE_MAPPING.get(inner_type)
        if marshmallow_field_cls is None:
            raise ValueError(f"Unsupported field type: {inner_type}")
        return MarshmallowFieldInfo(field=marshmallow_field_cls)


class MarshmallowSchemaGenerator:

    def __init__(
        self,
        pydantic_model_cls: type[BaseModel],
    ):
        self.pydantic_model_cls = pydantic_model_cls

    @staticmethod
    def process_field(model_field: FieldInfo):
        processor = FieldProcessor(model_field)
        return processor.process_field()

    def generate_marshmallow_schema(self) -> type[Schema]:
        schema_fields = {}

        for field_name, model_field in self.pydantic_model_cls.model_fields.items():
            marshmallow_field = self.process_field(model_field)
            schema_fields[field_name] = marshmallow_field

        return type(
            f"{self.pydantic_model_cls.__name__}AutoSchema", (Schema,), schema_fields
        )


def generate_marshmallow_schema(pydantic_model_cls: type[BaseModel]) -> type[Schema]:
    generator = MarshmallowSchemaGenerator(pydantic_model_cls)
    try:
        return generator.generate_marshmallow_schema()
    except ValueError as e:
        raise ValueError(
            f"Failed to generate marshmallow schema " f"for {pydantic_model_cls}: {e}"
        )
