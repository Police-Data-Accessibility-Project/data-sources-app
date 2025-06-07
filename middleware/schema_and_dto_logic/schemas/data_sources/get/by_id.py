from marshmallow import fields

from middleware.schema_and_dto_logic.common_response_schemas import MessageSchema
from middleware.schema_and_dto_logic.schemas.data_sources.get.base import (
    DataSourceGetSchema,
)
from middleware.schema_and_dto_logic.util import get_json_metadata


class DataSourcesGetByIDSchema(MessageSchema):
    data = fields.Nested(
        DataSourceGetSchema,
        metadata=get_json_metadata("The result"),
    )
