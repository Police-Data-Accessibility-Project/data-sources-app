from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
    MetadataInfo,
)


class TestEnum(Enum):
    ALPHA = "alpha"
    BETA = "beta"
    GAMMA = "gamma"


class TestDTO(BaseModel):
    str_: Optional[str] = Field(
        default=None,
        description="A string field",
        json_schema_extra=MetadataInfo(required=False),
    )
    int_: Optional[int] = Field(
        description="An integer field",
        json_schema_extra=MetadataInfo(required=True),
    )
    float_: float = Field(
        description="A float field",
        json_schema_extra=MetadataInfo(required=False),
    )
    bool_: bool = Field(
        default=False,
        description="A boolean field",
        json_schema_extra=MetadataInfo(required=False),
    )
    enum_: TestEnum = Field(
        default=TestEnum.ALPHA,
        description="An enum field",
        json_schema_extra=MetadataInfo(required=False),
    )


def test_pydantic_to_marshmallow():
    SchemaAuto = generate_marshmallow_schema(TestDTO)
    schema = SchemaAuto()

    d = schema.load({"int_": None, "float_": 1.0})
    assert d["bool_"] is not None
    assert not d["bool_"]
    assert d["enum_"] == TestEnum.ALPHA

    d = schema.load({"int_": 1, "enum_": "beta"})
    assert d["enum_"] == TestEnum.BETA

    print(schema.fields)
