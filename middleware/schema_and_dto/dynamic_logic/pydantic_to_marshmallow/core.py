from marshmallow import Schema
from pydantic import BaseModel

from middleware.schema_and_dto.dynamic_logic.pydantic_to_marshmallow.generator.core import (
    MarshmallowSchemaGenerator,
)


def generate_marshmallow_schema(pydantic_model_cls: type[BaseModel]) -> type[Schema]:
    generator = MarshmallowSchemaGenerator(pydantic_model_cls)
    try:
        return generator.generate_marshmallow_schema()
    except ValueError as e:
        raise ValueError(
            f"Failed to generate marshmallow schema " f"for {pydantic_model_cls}: {e}"
        )
