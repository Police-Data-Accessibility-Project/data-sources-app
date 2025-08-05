from marshmallow import Schema, fields

from middleware.schema_and_dto.util import get_json_metadata


class DataSourcesMapResponseInnerSchema(Schema):
    data_source_id = fields.Integer(
        metadata=get_json_metadata("The id of the data source")
    )
    name = fields.String(metadata=get_json_metadata("The name of the data source"))
    location_id = fields.Integer(
        metadata=get_json_metadata("The id of the associated location")
    )
    agency_id = fields.Integer(
        metadata=get_json_metadata("The id of the associated agency")
    )
    agency_name = fields.String(
        metadata=get_json_metadata("The name of the associated agency")
    )
    state_iso = fields.String(
        metadata=get_json_metadata("The ISO code of the state"),
    )
    municipality = fields.String(
        metadata=get_json_metadata("The name of the municipality"), allow_none=True
    )
    county_name = fields.String(
        metadata=get_json_metadata("The name of the county"), allow_none=True
    )
    record_type = fields.String(metadata=get_json_metadata("The type of the record"))
    lat = fields.Float(metadata=get_json_metadata("The latitude of the data source"), allow_none=True)
    lng = fields.Float(metadata=get_json_metadata("The longitude of the data source"), allow_none=True)
