from marshmallow import fields

from middleware.schema_and_dto_logic.common_response_schemas import (
    MessageSchema,
)
from middleware.schema_and_dto_logic.schemas.data_sources.map.inner import (
    DataSourcesMapResponseInnerSchema,
)
from middleware.schema_and_dto_logic.util import get_json_metadata


class DataSourcesMapResponseSchema(MessageSchema):
    data = fields.List(
        fields.Nested(
            DataSourcesMapResponseInnerSchema(),
            metadata=get_json_metadata("The list of results"),
        ),
        metadata=get_json_metadata("The list of results"),
    )
