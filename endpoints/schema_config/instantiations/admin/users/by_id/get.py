from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.dtos.common.base import GetByIDBaseDTO
from middleware.schema_and_dto.schemas.admin.by_id import (
    AdminUsersGetByIDResponseSchema,
)
from middleware.schema_and_dto.schemas.common.base import GetByIDBaseSchema

AdminUsersByIDGetEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=GetByIDBaseSchema(),
    input_dto_class=GetByIDBaseDTO,
    primary_output_schema=AdminUsersGetByIDResponseSchema(),
)
