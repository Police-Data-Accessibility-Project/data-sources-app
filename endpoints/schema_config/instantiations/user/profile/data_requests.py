from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.dtos.common.base import (
    GetManyRequestsBaseSchema,
    GetManyBaseDTO,
)
from middleware.schema_and_dto.schemas.data_requests.get.many.response import (
    GetManyDataRequestsResponseSchema,
)

UserProfileDataRequestsGetEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=GetManyRequestsBaseSchema(),
    input_dto_class=GetManyBaseDTO,
    primary_output_schema=GetManyDataRequestsResponseSchema(
        exclude=["data.internal_notes"]
    ),
)
