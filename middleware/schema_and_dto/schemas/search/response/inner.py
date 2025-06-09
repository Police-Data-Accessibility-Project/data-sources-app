from marshmallow import Schema, fields

from middleware.schema_and_dto.util import get_json_metadata


class SearchResultsInnerSchema(Schema):
    id = fields.Int(
        required=True,
        metadata=get_json_metadata("The ID of the search."),
    )
    agency_name = fields.Str(
        required=True,
        metadata=get_json_metadata("The name of the agency."),
    )
    municipality = fields.Str(
        required=True,
        allow_none=True,
        metadata=get_json_metadata("The name of the municipality."),
    )
    state_iso = fields.Str(
        required=True,
        metadata=get_json_metadata("The ISO code of the state."),
    )
    data_source_name = fields.Str(
        required=True,
        metadata=get_json_metadata("The name of the data source."),
    )
    description = fields.Str(
        required=True,
        allow_none=True,
        metadata=get_json_metadata("The description of the search."),
    )
    record_type = fields.Str(
        required=True,
        metadata=get_json_metadata("The type of the record."),
    )
    source_url = fields.Str(
        required=True,
        metadata=get_json_metadata("The URL of the data source."),
    )
    record_formats = fields.List(
        fields.Str(
            required=True,
            metadata=get_json_metadata("The record formats of the search."),
        ),
        allow_none=True,
        metadata=get_json_metadata("The record formats of the search."),
    )
    coverage_start = fields.Str(
        required=True,
        allow_none=True,
        metadata=get_json_metadata("The start date of the search."),
    )
    coverage_end = fields.Str(
        required=True,
        metadata=get_json_metadata("The end date of the search."),
        allow_none=True,
    )
    agency_supplied = fields.Bool(
        required=True,
        metadata=get_json_metadata("Whether the agency supplied the data."),
    )
    jurisdiction_type = fields.Str(
        required=True,
        metadata=get_json_metadata("The type of the jurisdiction."),
    )
