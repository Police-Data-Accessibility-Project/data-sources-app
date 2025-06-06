from typing import Optional

from pydantic import BaseModel, Field

from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)


class TestDTO(BaseModel):
    password: Optional[str] = Field(
        default=None, description="The new password of the admin user"
    )


def test_pydantic_to_marshmallow():
    SchemaAuto = generate_marshmallow_schema(TestDTO)
    schema = SchemaAuto()

    print(schema.fields)
