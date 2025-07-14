from endpoints.schema_config.helpers import get_post_resource_endpoint_schema_config
from endpoints.instantiations.data_requests_.post.dto import DataRequestsPostDTO
from endpoints.instantiations.data_requests_.post.schema import DataRequestsPostSchema

DataRequestsPostEndpointSchemaConfig = get_post_resource_endpoint_schema_config(
    input_schema=DataRequestsPostSchema(),
    input_dto_class=DataRequestsPostDTO,
)
