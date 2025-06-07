from middleware.schema_and_dto_logic.dtos.agencies_dtos import AgencyInfoPutDTO
from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)

AgencyInfoPutSchema = generate_marshmallow_schema(AgencyInfoPutDTO)
