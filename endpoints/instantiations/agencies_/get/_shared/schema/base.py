from endpoints.instantiations.agencies_.get._shared.dto.base import AgenciesGetDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)


AgenciesGetSchema = pydantic_to_marshmallow(AgenciesGetDTO)
