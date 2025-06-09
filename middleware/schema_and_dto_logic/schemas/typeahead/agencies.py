from marshmallow import fields, validate, Schema

from middleware.schema_and_dto_logic.schemas.typeahead._helpers import (
    JURISDICTION_TYPES,
)
from middleware.schema_and_dto_logic.schemas.typeahead.base import (
    TypeaheadBaseResponseSchema,
)
from utilities.enums import SourceMappingEnum


class TypeaheadAgenciesResponseSchema(TypeaheadBaseResponseSchema):
    id = fields.Integer(
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
            "example": "Springfield County Sheriff's Office",
        },
    )
    jurisdiction_type = fields.String(
        required=True,
        validate=validate.OneOf(JURISDICTION_TYPES),
        metadata={
            "source": SourceMappingEnum.JSON,
            "description": "The jurisdiction type.",
            "example": "school",
        },
    )


class TypeaheadAgenciesOuterResponseSchema(Schema):
    # pass
    suggestions = fields.List(
        cls_or_instance=fields.Nested(
            nested=TypeaheadAgenciesResponseSchema(exclude=["state_name"]),
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
