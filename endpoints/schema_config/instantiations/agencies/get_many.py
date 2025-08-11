from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.dtos.agencies.get_many import AgenciesGetManyDTO
from endpoints.instantiations.agencies_.get.many.schemas.requests import (
    GetManyAgenciesRequestsSchema,
)
from endpoints.instantiations.agencies_.get.many.schemas.response import (
    AgenciesGetManyResponseSchema,
)

AgenciesGetManyEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=GetManyAgenciesRequestsSchema(),
    primary_output_schema=AgenciesGetManyResponseSchema(),
    input_dto_class=AgenciesGetManyDTO,
)
