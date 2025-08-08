from marshmallow import Schema, fields
from marshmallow.fields import Nested

from middleware.schema_and_dto.schemas.locations.map.response import (
    LocationsMapResponseSchema,
)
from middleware.schema_and_dto.util import get_json_metadata


class FederalSourcesResponseInnerSchema(Schema):
    agency_name = fields.Str(
        required=True,
        metadata=get_json_metadata("The name of the federal source"),
    )
    data_source_name = fields.Str(
        required=True,
        metadata=get_json_metadata("The ID of the federal source"),
    )
    source_url = fields.Str(
        required=True,
        metadata=get_json_metadata("The URL of the federal source"),
    )
    source_id = fields.Int(
        required=True,
        metadata=get_json_metadata("The ID of the federal source"),
    )


class DataMapResponseSchema(Schema):
    locations = Nested(
        LocationsMapResponseSchema(),
        required=True,
        metadata=get_json_metadata("All locations"),
    )
    sources = fields.List(
        fields.Nested(
            FederalSourcesResponseInnerSchema(),
            required=True,
            metadata=get_json_metadata("All federal sources"),
        ),
        required=True,
        metadata=get_json_metadata("All federal sources"),
    )
