from endpoints.schema_config.helpers import get_get_by_id_endpoint_schema_config
from middleware.schema_and_dto.schemas.data_requests.get.by_id.response import (
    GetByIDDataRequestsResponseSchema,
)

DataRequestsByIDGetEndpointSchemaConfig = get_get_by_id_endpoint_schema_config(
    primary_output_schema=GetByIDDataRequestsResponseSchema(),
)
