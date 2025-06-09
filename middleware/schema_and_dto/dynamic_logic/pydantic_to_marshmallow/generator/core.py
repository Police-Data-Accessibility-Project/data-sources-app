from marshmallow import Schema
from pydantic import BaseModel
from pydantic.fields import FieldInfo

from middleware.schema_and_dto.dynamic_logic.pydantic_to_marshmallow.generator.field_processor import (
    FieldProcessor,
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
