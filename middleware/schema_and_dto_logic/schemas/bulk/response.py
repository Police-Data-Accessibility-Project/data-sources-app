from marshmallow import fields

from middleware.schema_and_dto_logic.schemas.common.common_response_schemas import (
    MessageSchema,
)
from middleware.schema_and_dto_logic.util import get_json_metadata


class BatchPostResponseSchema(MessageSchema):
    ids = fields.List(
        fields.Integer(metadata=get_json_metadata("The ids of the resources created")),
        required=True,
        metadata=get_json_metadata("The ids of the resources created"),
    )
    errors = fields.Dict(
        required=True,
        metadata=get_json_metadata("The errors associated with resources not created"),
    )
