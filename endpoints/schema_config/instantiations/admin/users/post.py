from endpoints.schema_config.helpers import get_post_resource_endpoint_schema_config
from middleware.schema_and_dto.dtos.admin.post import AdminUserPostDTO
from middleware.schema_and_dto.schemas.admin.post import AdminUsersPostSchema

AdminUsersPostEndpointSchemaConfig = get_post_resource_endpoint_schema_config(
    input_schema=AdminUsersPostSchema(),
    input_dto_class=AdminUserPostDTO,
)
