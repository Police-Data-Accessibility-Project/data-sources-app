from endpoints.instantiations.data_requests_.post.dto import DataRequestsPostDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)

DataRequestsPostSchema = pydantic_to_marshmallow(DataRequestsPostDTO)
