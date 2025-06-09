from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.dtos.agencies.get_many import AgenciesGetManyDTO
from middleware.schema_and_dto.schemas.agencies.get.many.requests import (
    GetManyAgenciesRequestsSchema,
)
from middleware.schema_and_dto.schemas.agencies.get.many.response import (
    AgenciesGetManyResponseSchema,
)

AgenciesGetManyEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=GetManyAgenciesRequestsSchema(),
    primary_output_schema=AgenciesGetManyResponseSchema(),
    input_dto_class=AgenciesGetManyDTO,
)
