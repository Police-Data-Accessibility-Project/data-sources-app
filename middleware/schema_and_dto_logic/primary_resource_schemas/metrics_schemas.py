from marshmallow import Schema, fields

from middleware.schema_and_dto_logic.util import get_json_metadata


class MetricsGetResponseSchema(Schema):
    source_count = fields.Int(metadata=get_json_metadata("The number of data sources"))
    agency_count = fields.Int(metadata=get_json_metadata("The number of agencies"))
    county_count = fields.Int(metadata=get_json_metadata("The number of counties"))
    state_count = fields.Int(metadata=get_json_metadata("The number of states"))
