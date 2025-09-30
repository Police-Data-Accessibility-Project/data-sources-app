from marshmallow import Schema, fields

from endpoints.instantiations.source_collector.meta_urls.post.dtos.request import (
    SourceCollectorMetaURLPostRequestInnerDTO,
)
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)
from middleware.schema_and_dto.util import get_json_metadata

SourceCollectorMetaURLPostRequestInnerSchema = pydantic_to_marshmallow(
    SourceCollectorMetaURLPostRequestInnerDTO
)


class SourceCollectorMetaURLPostRequestSchema(Schema):
    meta_urls = fields.List(
        fields.Nested(
            SourceCollectorMetaURLPostRequestInnerSchema(),
            required=True,
            metadata=get_json_metadata("The Meta URLs associated with the request"),
        ),
        required=True,
        metadata=get_json_metadata("The Meta URLs associated with the request"),
    )
