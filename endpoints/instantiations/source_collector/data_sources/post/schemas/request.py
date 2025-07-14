from marshmallow import Schema, fields

from endpoints.instantiations.source_collector.data_sources.post.dtos.request import (
    SourceCollectorPostRequestInnerDTO,
)
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)
from middleware.schema_and_dto.util import get_json_metadata


SourceCollectorPostRequestInnerSchema = pydantic_to_marshmallow(
    SourceCollectorPostRequestInnerDTO
)


class SourceCollectorPostRequestSchema(Schema):
    data_sources = fields.List(
        fields.Nested(
            SourceCollectorPostRequestInnerSchema(),
            required=True,
            metadata=get_json_metadata("The data sources associated with the request"),
        ),
        required=True,
        metadata=get_json_metadata("The data sources associated with the request"),
    )
