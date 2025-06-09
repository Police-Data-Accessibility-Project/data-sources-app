from marshmallow import Schema, fields

from middleware.schema_and_dto_logic.util import get_json_metadata


class StatesLocationsMapInnerSchema(Schema):
    source_count = fields.Int(
        metadata=get_json_metadata("The number of data sources for the state")
    )
    name = fields.Str(metadata=get_json_metadata("The name of the state"))
    state_iso = fields.Str(metadata=get_json_metadata("The iso code of the state"))
    location_id = fields.Integer(metadata=get_json_metadata("The id of the state"))
