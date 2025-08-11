from marshmallow import fields

from middleware.schema_and_dto.schemas.common.common_response_schemas import (
    MessageSchema,
)
from endpoints.instantiations.data_sources_.get._shared.schema.base import (
    DataSourceGetSchema,
)
from middleware.schema_and_dto.util import get_json_metadata


class DataSourcesGetByIDSchema(MessageSchema):
    data = fields.Nested(
        DataSourceGetSchema,
        metadata=get_json_metadata("The result"),
    )
