from middleware.schema_and_dto.schemas.schema_helpers import (
    create_get_by_id_schema,
)
from endpoints.instantiations.data_requests_._shared.schemas.get import DataRequestsGetSchemaBase

GetByIDDataRequestsResponseSchema = create_get_by_id_schema(
    data_schema=DataRequestsGetSchemaBase,
    description="The data request result",
)
