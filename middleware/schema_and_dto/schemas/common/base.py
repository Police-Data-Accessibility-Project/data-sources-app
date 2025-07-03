from middleware.schema_and_dto.dtos.common.base import GetByIDBaseDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)

GetByIDBaseSchema = pydantic_to_marshmallow(GetByIDBaseDTO)
