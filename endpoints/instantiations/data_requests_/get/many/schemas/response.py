from endpoints.instantiations.data_requests_.get.many.dtos.response import (
    GetManyDataRequestsResponseDTO,
)
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)

GetManyDataRequestsResponseSchema = pydantic_to_marshmallow(
    GetManyDataRequestsResponseDTO
)
