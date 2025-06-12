from endpoints.schema_config.helpers import get_put_resource_endpoint_schema_config
from middleware.schema_and_dto.dtos.data_requests.put import DataRequestsPutOuterDTO
from middleware.schema_and_dto.schemas.data_requests.put import DataRequestsPutSchema

DataRequestsByIDPutEndpointSchemaConfig = get_put_resource_endpoint_schema_config(
    input_schema=DataRequestsPutSchema(),
    input_dto_class=DataRequestsPutOuterDTO,
)
