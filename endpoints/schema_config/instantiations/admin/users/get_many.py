from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.dtos.common.base import (
    GetManyRequestsBaseSchema,
    GetManyBaseDTO,
)
from middleware.schema_and_dto.schemas.admin.get_many import (
    AdminUsersGetManyResponseSchema,
)

AdminUsersGetManyEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=GetManyRequestsBaseSchema(),
    input_dto_class=GetManyBaseDTO,
    primary_output_schema=AdminUsersGetManyResponseSchema(),
)
