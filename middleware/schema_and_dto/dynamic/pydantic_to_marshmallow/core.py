from marshmallow import Schema
from pydantic import BaseModel

from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.generator.core import (
    MarshmallowSchemaGenerator,
)


def pydantic_to_marshmallow(pydantic_model_cls: type[BaseModel]) -> type[Schema]:
    generator = MarshmallowSchemaGenerator(pydantic_model_cls)
    try:
        return generator.generate_marshmallow_schema()
    except ValueError as e:
        raise ValueError(
            f"Failed to generate marshmallow schema for {pydantic_model_cls}: {e}"
        )
