from endpoints.instantiations.data_requests_.get.many.dtos.response import GetManyDataRequestsResponseDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import pydantic_to_marshmallow
from middleware.schema_and_dto.schemas.schema_helpers import (
    create_get_many_schema,
)
from endpoints.instantiations.data_requests_._shared.schemas.get import DataRequestsGetSchemaBase

GetManyDataRequestsResponseSchema = create_get_many_schema(
    data_list_schema=DataRequestsGetSchemaBase,
    description="The list of data requests",
)

# GetManyDataRequestsResponseSchema = pydantic_to_marshmallow(
#     GetManyDataRequestsResponseDTO
# )
