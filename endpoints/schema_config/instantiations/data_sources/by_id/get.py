from endpoints.schema_config.helpers import get_get_by_id_endpoint_schema_config
from middleware.schema_and_dto.schemas.data_sources.get.by_id import (
    DataSourcesGetByIDSchema,
)

DataSourcesByIDGetEndpointSchemaConfig = get_get_by_id_endpoint_schema_config(
    primary_output_schema=DataSourcesGetByIDSchema(),
)
