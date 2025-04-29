from marshmallow import Schema, fields

from middleware.schema_and_dto_logic.common_fields import (
    PAGE_FIELD,
    SORT_BY_FIELD,
    SORT_ORDER_FIELD,
)
from middleware.schema_and_dto_logic.util import get_json_metadata


class MetricsGetResponseSchema(Schema):
    source_count = fields.Int(metadata=get_json_metadata("The number of data sources"))
    agency_count = fields.Int(metadata=get_json_metadata("The number of agencies"))
    county_count = fields.Int(metadata=get_json_metadata("The number of counties"))
    state_count = fields.Int(metadata=get_json_metadata("The number of states"))


class MetricsFollowedSearchesBreakdownInnerSchema(Schema):
    location_name = fields.Str(metadata=get_json_metadata("The name of the location"))
    location_id = fields.Int(metadata=get_json_metadata("The id of the location"))
    follower_count = fields.Int(metadata=get_json_metadata("The number of searches"))
    source_count = fields.Int(metadata=get_json_metadata("The number of data sources"))
    request_count = fields.Int(metadata=get_json_metadata("The number of requests"))
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


class MetricsFollowedSearchesBreakdownRequestSchema(Schema):
    page = PAGE_FIELD
    sort_by = SORT_BY_FIELD
    sort_order = SORT_ORDER_FIELD


class MetricsFollowedSearchesAggregateResponseSchema(Schema):
    total_followers = fields.Int(
        metadata=get_json_metadata("The total number of followers")
    )
    total_followed_searches = fields.Int(
        metadata=get_json_metadata("The total number of followed searches")
    )
    last_notification_date = fields.Date(
        metadata=get_json_metadata("The date that notifications were sent out"),
        allow_none=True,
    )
