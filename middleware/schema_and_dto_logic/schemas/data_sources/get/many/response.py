from marshmallow import fields

from middleware.schema_and_dto_logic.common_response_schemas import (
    GetManyResponseSchemaBase,
)
from middleware.schema_and_dto_logic.schemas.data_sources.get.base import (
    DataSourceGetSchema,
)
from middleware.schema_and_dto_logic.util import get_json_metadata


class DataSourcesGetManySchema(GetManyResponseSchemaBase):
    data = fields.List(
        cls_or_instance=fields.Nested(
            nested=DataSourceGetSchema,
            metadata=get_json_metadata("The list of results"),
        ),
        metadata=get_json_metadata("The list of results"),
    )
