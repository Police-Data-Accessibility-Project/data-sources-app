from endpoints.schema_config.helpers import get_get_by_id_endpoint_schema_config
from endpoints.instantiations.agencies_.get.many.schemas.response import (
    AgenciesGetManyResponseSchema,
)

DataSourcesRelatedAgenciesGet = get_get_by_id_endpoint_schema_config(
    primary_output_schema=AgenciesGetManyResponseSchema(exclude=["data.data_sources"]),
)
