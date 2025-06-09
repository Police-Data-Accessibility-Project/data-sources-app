from endpoints.schema_config.helpers import get_post_resource_endpoint_schema_config
from middleware.schema_and_dto.dtos.data_requests.post import DataRequestsPostDTO
from middleware.schema_and_dto.schemas.data_requests.post import DataRequestsPostSchema

DataRequestsPostEndpointSchemaConfig = get_post_resource_endpoint_schema_config(
    input_schema=DataRequestsPostSchema(),
    input_dto_class=DataRequestsPostDTO,
)
