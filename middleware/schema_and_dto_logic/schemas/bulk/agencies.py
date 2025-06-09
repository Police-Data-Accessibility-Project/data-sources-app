from middleware.schema_and_dto_logic.schemas.bulk.flat.agencies import (
    AgenciesPostRequestFlatBaseSchema,
)
from middleware.schema_and_dto_logic.schemas.bulk.request import BatchRequestSchema


class AgenciesPostBatchRequestSchema(
    BatchRequestSchema, AgenciesPostRequestFlatBaseSchema
):
    pass
