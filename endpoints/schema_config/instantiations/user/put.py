from endpoints.schema_config.helpers import get_put_resource_endpoint_schema_config
from middleware.schema_and_dto.dtos.user_profile import UserPutDTO
from middleware.schema_and_dto.schemas.user.put import UserPutSchema

UserPutEndpointSchemaConfig = get_put_resource_endpoint_schema_config(
    input_schema=UserPutSchema(),
    input_dto_class=UserPutDTO,
)
