from marshmallow import fields, validate

from endpoints.instantiations.source_collector.data_sources.post.dtos.response import (
    SourceCollectorPostResponseInnerDTO,
)
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)
from middleware.schema_and_dto.schemas.common.common_response_schemas import (
    MessageSchema,
)


from middleware.schema_and_dto.util import get_json_metadata

SourceCollectorPostResponseInnerSchema = generate_marshmallow_schema(
    SourceCollectorPostResponseInnerDTO
)


class SourceCollectorPostResponseSchema(MessageSchema):
    data_sources = fields.List(
        fields.Nested(
            SourceCollectorPostResponseInnerSchema(),
            required=True,
            metadata=get_json_metadata(
                "The data sources associated with the data request"
            ),
        ),
        required=True,
        metadata=get_json_metadata("The data sources associated with the data request"),
        validate=validate.Length(min=1, max=100),
    )
