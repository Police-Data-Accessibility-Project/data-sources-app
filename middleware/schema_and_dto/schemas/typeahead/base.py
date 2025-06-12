from marshmallow import Schema, fields

from utilities.enums import SourceMappingEnum


class TypeaheadBaseResponseSchema(Schema):
    state_name = fields.String(
        required=True,
        allow_none=True,
        metadata={
            "source": SourceMappingEnum.JSON,
            "description": "The state of the suggestion",
            "example": "Pennsylvania",
        },
    )
    state_iso = fields.String(
        required=True,
        allow_none=True,
        metadata={
            "source": SourceMappingEnum.JSON,
            "description": "The state ISO of the suggestion",
            "example": "PA",
        },
    )
    county_name = fields.String(
        required=True,
        metadata={
            "source": SourceMappingEnum.JSON,
            "description": "The county of the suggestion",
            "example": "Allegheny",
        },
        allow_none=True,
    )
    locality_name = fields.String(
        required=True,
        metadata={
            "source": SourceMappingEnum.JSON,
            "description": "The locality of the suggestion",
            "example": "Pittsburgh",
        },
        allow_none=True,
    )
