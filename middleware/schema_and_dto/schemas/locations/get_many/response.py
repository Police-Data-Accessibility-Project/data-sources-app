from marshmallow import fields, Schema

from middleware.schema_and_dto.schemas.locations.lat_lng import LatLngSchema
from middleware.schema_and_dto.schemas.locations.info.expanded import (
    LocationInfoExpandedSchema,
)
from middleware.schema_and_dto.util import get_json_metadata


class LocationInfoGetManyInnerSchema(LocationInfoExpandedSchema):
    coordinates = fields.Nested(
        LatLngSchema(),
        required=True,
        metadata=get_json_metadata("The latitude and longitude of the location"),
    )


class LocationsGetManyResponseSchema(Schema):
    results = fields.List(
        fields.Nested(
            LocationInfoGetManyInnerSchema(),
            required=True,
            metadata=get_json_metadata("The list of results"),
        ),
        required=True,
        metadata=get_json_metadata("The list of results"),
    )
