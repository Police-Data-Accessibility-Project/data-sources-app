from marshmallow import Schema, fields

from middleware.schema_and_dto_logic.schemas.locations.lat_lng import LatLngSchema
from middleware.schema_and_dto_logic.util import get_json_metadata


class LocalitiesLocationsMapInnerSchema(Schema):
    source_count = fields.Int(
        metadata=get_json_metadata("The number of data sources for the locality")
    )
    name = fields.Str(metadata=get_json_metadata("The name of the locality"))
    location_id = fields.Integer(metadata=get_json_metadata("The id of the locality"))
    county_name = fields.Str(metadata=get_json_metadata("The name of the county"))
    county_fips = fields.Str(metadata=get_json_metadata("The fips code of the county"))
    state_iso = fields.Str(metadata=get_json_metadata("The iso code of the state"))
    coordinates = fields.Nested(
        LatLngSchema(),
        required=True,
        metadata=get_json_metadata("The latitude and longitude of the location"),
    )
