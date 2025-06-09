from middleware.schema_and_dto.schemas.schema_helpers import (
    create_get_many_schema,
)
from middleware.schema_and_dto.schemas.data_requests.get.base import (
    DataRequestsGetSchemaBase,
)

GetManyDataRequestsResponseSchema = create_get_many_schema(
    data_list_schema=DataRequestsGetSchemaBase,
    description="The list of data requests",
)
