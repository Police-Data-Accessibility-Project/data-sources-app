from endpoints.schema_config.helpers import get_get_by_id_endpoint_schema_config
from middleware.schema_and_dto.schemas.data_sources.get.many.response import (
    DataSourcesGetManySchema,
)

DataRequestsRelatedSourcesGetEndpointSchemaConfig = (
    get_get_by_id_endpoint_schema_config(
        primary_output_schema=DataSourcesGetManySchema(
            exclude=["data.agencies"], partial=True
        ),
    )
)
