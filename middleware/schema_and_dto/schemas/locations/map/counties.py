from marshmallow import Schema, fields

from middleware.schema_and_dto.util import get_json_metadata


class CountiesLocationsMapInnerSchema(Schema):
    source_count = fields.Int(
        metadata=get_json_metadata("The number of data sources for the county")
    )
    name = fields.Str(metadata=get_json_metadata("The name of the county"))
    location_id = fields.Integer(metadata=get_json_metadata("The id of the county"))
    state_iso = fields.Str(metadata=get_json_metadata("The iso code of the state"))
    fips = fields.Str(metadata=get_json_metadata("The fips code of the county"))
