from marshmallow import fields

from middleware.schema_and_dto.schemas.common.base import GetByIDBaseSchema
from utilities.enums import SourceMappingEnum

# Base Schema


class AgenciesRelatedLocationSchema(GetByIDBaseSchema):
    location_id = fields.Integer(
        required=True,
        metadata={
            "description": "The id of the related location.",
            "source": SourceMappingEnum.PATH,
        },
    )
