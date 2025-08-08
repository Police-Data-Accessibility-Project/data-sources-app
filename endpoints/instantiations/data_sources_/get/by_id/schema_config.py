from endpoints.schema_config.helpers import get_get_by_id_endpoint_schema_config
from endpoints.instantiations.data_sources_.get.by_id.schema import (
    DataSourcesGetByIDSchema,
)

DataSourcesByIDGetEndpointSchemaConfig = get_get_by_id_endpoint_schema_config(
    primary_output_schema=DataSourcesGetByIDSchema(),
)
