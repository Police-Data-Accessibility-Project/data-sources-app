from marshmallow.fields import Field
from pydantic import BaseModel, Field as PydanticField


class MarshmallowFieldInfo(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    field: type[Field]
    field_kwargs: dict = PydanticField(default_factory=dict)
