from marshmallow import fields

from middleware.schema_and_dto.schemas.common.common_response_schemas import (
    MessageSchema,
)
from middleware.schema_and_dto.util import get_json_metadata


class BatchPostResponseSchema(MessageSchema):
    ids = fields.List(
        fields.Integer(metadata=get_json_metadata("The ids of the endpoints created")),
        required=True,
        metadata=get_json_metadata("The ids of the endpoints created"),
    )
    errors = fields.Dict(
        required=True,
        metadata=get_json_metadata("The errors associated with endpoints not created"),
    )
