from marshmallow import Schema, fields, validate

from utilities.enums import SourceMappingEnum

JURISDICTION_TYPES = [
    "school",
    None,
    "county",
    "local",
    "port",
    "tribal",
    "transit",
    "state",
    "federal",
]


class TypeaheadBaseResponseSchema(Schema):
    state = fields.String(
        required=True,
        metadata={
            "source": SourceMappingEnum.JSON,
            "description": "The state of the suggestion",
            "example": "Pennsylvania",
        },
    )
    county = fields.String(
        required=True,
        metadata={
            "source": SourceMappingEnum.JSON,
            "description": "The county of the suggestion",
            "example": "Allegheny",
        },
        allow_none=True,
    )
    locality = fields.String(
        required=True,
        metadata={
            "source": SourceMappingEnum.JSON,
            "description": "The locality of the suggestion",
            "example": "Pittsburgh",
        },
        allow_none=True,
    )


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


class TypeaheadAgenciesResponseSchema(TypeaheadBaseResponseSchema):
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
            nested=TypeaheadAgenciesResponseSchema,
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


class TypeaheadLocationsOuterResponseSchema(Schema):

    suggestions = fields.List(
        cls_or_instance=fields.Nested(
            nested=TypeaheadLocationsResponseSchema,
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
