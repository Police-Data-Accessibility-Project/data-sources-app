from marshmallow import Schema, fields, validate

from db.enums import LocationType
from utilities.enums import SourceMappingEnum


class LocationsGetManyRequestSchema(Schema):
    page = fields.Integer(
        validate=validate.Range(min=1),
        load_default=1,
        metadata={
            "description": "The page number of the results to retrieve. Begins at 1.",
            "source": SourceMappingEnum.QUERY_ARGS,
        },
    )
    type = fields.Enum(
        required=False,
        allow_none=True,
        enum=LocationType,
        by_value=fields.Str,
        metadata={
            "description": "The type of location. ",
            "source": SourceMappingEnum.QUERY_ARGS,
        },
    )
    has_coordinates = fields.Boolean(
        required=False,
        allow_none=True,
        metadata={
            "description": "Whether or not the location has coordinates",
            "source": SourceMappingEnum.QUERY_ARGS,
        },
    )
