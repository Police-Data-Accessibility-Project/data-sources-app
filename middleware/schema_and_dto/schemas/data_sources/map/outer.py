from marshmallow import fields

from middleware.schema_and_dto.schemas.common.common_response_schemas import (
    MessageSchema,
)
from middleware.schema_and_dto.schemas.data_sources.map.inner import (
    DataSourcesMapResponseInnerSchema,
)
from middleware.schema_and_dto.util import get_json_metadata


class DataSourcesMapResponseSchema(MessageSchema):
    data = fields.List(
        fields.Nested(
            DataSourcesMapResponseInnerSchema(),
            metadata=get_json_metadata("The list of results"),
        ),
        metadata=get_json_metadata("The list of results"),
    )
