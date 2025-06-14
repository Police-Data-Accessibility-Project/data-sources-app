from middleware.schema_and_dto.dynamic.csv_to_schema_conversion import (
    generate_flat_csv_schema,
)
from middleware.schema_and_dto.schemas.data_sources.post import (
    DataSourcesPostSchema,
)

DataSourcesPostRequestFlatBaseSchema = generate_flat_csv_schema(
    schema=DataSourcesPostSchema()
)
