from endpoints.schema_config.helpers import get_post_resource_endpoint_schema_config
from middleware.schema_and_dto.dtos.data_sources.post import DataSourcesPostDTO
from middleware.schema_and_dto.schemas.data_sources.post import DataSourcesPostSchema

DataSourcesPostEndpointSchemaConfig = get_post_resource_endpoint_schema_config(
    input_schema=DataSourcesPostSchema(),
    input_dto_class=DataSourcesPostDTO,
)
