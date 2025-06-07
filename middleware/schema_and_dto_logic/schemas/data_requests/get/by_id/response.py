from middleware.schema_and_dto_logic.schema_helpers import create_get_by_id_schema
from middleware.schema_and_dto_logic.schemas.data_requests.get.base import (
    DataRequestsGetSchemaBase,
)

GetByIDDataRequestsResponseSchema = create_get_by_id_schema(
    data_schema=DataRequestsGetSchemaBase,
    description="The data request result",
)
