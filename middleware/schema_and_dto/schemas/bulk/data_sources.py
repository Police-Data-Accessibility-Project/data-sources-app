from middleware.schema_and_dto.schemas.bulk.flat.data_sources import (
    DataSourcesPostRequestFlatBaseSchema,
)
from middleware.schema_and_dto.schemas.bulk.request import BatchRequestSchema


class DataSourcesPostBatchRequestSchema(
    BatchRequestSchema, DataSourcesPostRequestFlatBaseSchema
):
    pass
