from endpoints.schema_config.helpers import get_post_resource_endpoint_schema_config
from endpoints.instantiations.agencies_.post.dto import AgenciesPostDTO
from endpoints.instantiations.agencies_.post.schemas.outer import AgenciesPostSchema

AgenciesPostEndpointSchemaConfig = get_post_resource_endpoint_schema_config(
    input_schema=AgenciesPostSchema(),
    input_dto_class=AgenciesPostDTO,
)
