from marshmallow import fields, validate

from middleware.schema_and_dto_logic.schemas.common.common_response_schemas import (
    MessageSchema,
)
from middleware.schema_and_dto_logic.dtos.source_collector.post.response import (
    SourceCollectorPostResponseInnerDTO,
)
from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)
from middleware.schema_and_dto_logic.util import get_json_metadata

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
