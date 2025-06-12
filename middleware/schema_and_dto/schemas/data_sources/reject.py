from marshmallow import fields

from middleware.schema_and_dto.schemas.common.base import GetByIDBaseSchema
from middleware.schema_and_dto.util import get_json_metadata


class DataSourceRejectSchema(GetByIDBaseSchema):
    rejection_note = fields.String(
        metadata=get_json_metadata("Why the note was rejected.")
    )
