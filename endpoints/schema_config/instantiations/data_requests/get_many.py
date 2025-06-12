from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.dtos.data_requests.get_many import (
    GetManyDataRequestsRequestsDTO,
)
from middleware.schema_and_dto.schemas.data_requests.get.many.requests import (
    GetManyDataRequestsRequestsSchema,
)
from middleware.schema_and_dto.schemas.data_requests.get.many.response import (
    GetManyDataRequestsResponseSchema,
)

DataRequestsGetManyEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=GetManyDataRequestsRequestsSchema(),
    primary_output_schema=GetManyDataRequestsResponseSchema(),
    input_dto_class=GetManyDataRequestsRequestsDTO,
)
