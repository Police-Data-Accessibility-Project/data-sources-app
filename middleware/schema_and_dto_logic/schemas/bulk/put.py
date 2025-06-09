from marshmallow import fields

from middleware.schema_and_dto_logic.schemas.bulk.request import BatchRequestSchema
from middleware.schema_and_dto_logic.util import get_json_metadata


class BatchPutRequestSchema(BatchRequestSchema):
    id = fields.Integer(
        required=True, metadata=get_json_metadata("The id of the resource to update")
    )
