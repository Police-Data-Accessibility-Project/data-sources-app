from marshmallow import fields

from middleware.schema_and_dto.schemas.common.common_response_schemas import MessageSchema
from endpoints.instantiations.map.data_sources.schemas.inner import DataSourcesMapResponseInnerSchema
from middleware.schema_and_dto.util import get_json_metadata


class DataSourcesMapResponseSchema(MessageSchema):
    data = fields.List(
        fields.Nested(
            DataSourcesMapResponseInnerSchema(),
            metadata=get_json_metadata("The list of results"),
        ),
        metadata=get_json_metadata("The list of results"),
    )
