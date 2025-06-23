from marshmallow import fields

from middleware.schema_and_dto.schemas.bulk.request import BatchRequestSchema
from middleware.schema_and_dto.util import get_json_metadata


class BatchPutRequestSchema(BatchRequestSchema):
    id = fields.Integer(
        required=True, metadata=get_json_metadata("The id of the resource to update")
    )
