from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.dtos.common.base import (
    GetManyRequestsBaseSchema,
    GetManyBaseDTO,
)
from endpoints.instantiations.data_requests_.get.many.schemas.response import (
    GetManyDataRequestsResponseSchema,
)

UserProfileDataRequestsGetEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=GetManyRequestsBaseSchema(),
    input_dto_class=GetManyBaseDTO,
    primary_output_schema=GetManyDataRequestsResponseSchema(
        exclude=["data.internal_notes"]
    ),
)
