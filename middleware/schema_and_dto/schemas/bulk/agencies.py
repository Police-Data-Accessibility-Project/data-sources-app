from middleware.schema_and_dto.schemas.bulk.flat.agencies import (
    AgenciesPostRequestFlatBaseSchema,
)
from middleware.schema_and_dto.schemas.bulk.request import BatchRequestSchema


class AgenciesPostBatchRequestSchema(
    BatchRequestSchema, AgenciesPostRequestFlatBaseSchema
):
    pass
