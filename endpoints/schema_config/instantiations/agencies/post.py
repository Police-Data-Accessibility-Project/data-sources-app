from endpoints.schema_config.helpers import get_post_resource_endpoint_schema_config
from middleware.schema_and_dto.dtos.agencies.post import AgenciesPostDTO
from middleware.schema_and_dto.schemas.agencies.post import AgenciesPostSchema

AgenciesPostEndpointSchemaConfig = get_post_resource_endpoint_schema_config(
    input_schema=AgenciesPostSchema(),
    input_dto_class=AgenciesPostDTO,
)
