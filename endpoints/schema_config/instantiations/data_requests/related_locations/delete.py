from endpoints.schema_config.helpers import schema_config_with_message_output
from middleware.schema_and_dto.dtos.data_requests.by_id.locations import (
    RelatedLocationsByIDDTO,
)
from middleware.schema_and_dto.schemas.data_requests.related_location.add_remove import (
    DataRequestsRelatedLocationAddRemoveSchema,
)

DataRequestsRelatedLocationsDeleteEndpointSchemaConfig = (
    schema_config_with_message_output(
        input_schema=DataRequestsRelatedLocationAddRemoveSchema(),
        input_dto_class=RelatedLocationsByIDDTO,
    )
)
