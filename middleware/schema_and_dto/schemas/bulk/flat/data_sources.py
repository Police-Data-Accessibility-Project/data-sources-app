from middleware.schema_and_dto.dynamic_logic.dynamic_csv_to_schema_conversion_logic import (
    generate_flat_csv_schema,
)
from middleware.schema_and_dto.schemas.data_sources.post import (
    DataSourcesPostSchema,
)

DataSourcesPostRequestFlatBaseSchema = generate_flat_csv_schema(
    schema=DataSourcesPostSchema()
)
