from marshmallow import fields

from middleware.schema_and_dto_logic.common_schemas_and_dtos import GetByIDBaseSchema
from utilities.enums import SourceMappingEnum


class RelatedAgencyByIDSchema(GetByIDBaseSchema):
    agency_id = fields.Integer(
        required=True,
        metadata={
            "description": "The id of the related agency.",
            "source": SourceMappingEnum.PATH,
        },
    )
