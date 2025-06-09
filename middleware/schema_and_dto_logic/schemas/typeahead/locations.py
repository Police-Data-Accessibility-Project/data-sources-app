from marshmallow import fields, validate, Schema

from middleware.schema_and_dto_logic.schemas.typeahead.base import (
    TypeaheadBaseResponseSchema,
)
from utilities.enums import SourceMappingEnum


class TypeaheadLocationsResponseSchema(TypeaheadBaseResponseSchema):
    location_id = fields.Integer(
        required=True,
        metadata={
            "source": SourceMappingEnum.JSON,
            "description": "The id of the suggestion",
            "example": 1,
        },
    )
    display_name = fields.String(
        required=True,
        metadata={
            "source": SourceMappingEnum.JSON,
            "description": "The display name of the suggestion",
            "example": "Pittsburgh",
        },
    )
    type = fields.String(
        required=True,
        validate=validate.OneOf(["State", "County", "Locality"]),
        metadata={
            "source": SourceMappingEnum.JSON,
            "description": "The type of suggestion.",
            "example": "Locality",
        },
    )


class TypeaheadLocationsOuterResponseSchema(Schema):

    suggestions = fields.List(
        cls_or_instance=fields.Nested(
            nested=TypeaheadLocationsResponseSchema(exclude=["state_iso"]),
            required=True,
            metadata={
                "source": SourceMappingEnum.JSON,
                "description": "The suggestions for the given query",
            },
        ),
        metadata={
            "source": SourceMappingEnum.JSON,
            "description": "The suggestions for the given query",
        },
    )
