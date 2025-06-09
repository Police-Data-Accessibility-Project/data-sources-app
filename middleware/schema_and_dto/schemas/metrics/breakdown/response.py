from marshmallow import Schema, fields

from middleware.schema_and_dto.schemas.metrics._helpers import (
    get_count_field,
    get_change_field,
)
from middleware.schema_and_dto.util import get_json_metadata


class MetricsFollowedSearchesBreakdownInnerSchema(Schema):
    location_name = fields.Str(metadata=get_json_metadata("The name of the location"))
    location_id = fields.Int(metadata=get_json_metadata("The id of the location"))
    follower_count = get_count_field("followers")
    follower_change = get_change_field("followers")
    source_count = get_count_field("data sources")
    source_change = get_change_field("data sources")
    approved_requests_count = get_count_field("requests started")
    approved_requests_change = get_change_field("requests started")
    completed_requests_count = get_count_field("requests completed")
    completed_requests_change = get_change_field("requests completed")
    search_url = fields.Str(metadata=get_json_metadata("The url for the search"))


class MetricsFollowedSearchesBreakdownOuterSchema(Schema):
    results = fields.List(
        fields.Nested(
            MetricsFollowedSearchesBreakdownInnerSchema(),
            metadata=get_json_metadata("The list of results"),
        ),
        required=True,
        metadata=get_json_metadata("The list of results"),
    )
