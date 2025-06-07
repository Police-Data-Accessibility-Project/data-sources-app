from marshmallow import Schema, fields

from db.constants import (
    GET_METRICS_FOLLOWED_SEARCHES_BREAKDOWN_SORTABLE_COLUMNS,
)
from middleware.schema_and_dto_logic.common_fields import (
    PAGE_FIELD,
    SORT_ORDER_FIELD,
    get_sort_by_field,
)
from middleware.schema_and_dto_logic.util import get_json_metadata


class MetricsGetResponseSchema(Schema):
    source_count = fields.Int(metadata=get_json_metadata("The number of data sources"))
    agency_count = fields.Int(metadata=get_json_metadata("The number of agencies"))
    county_count = fields.Int(metadata=get_json_metadata("The number of counties"))
    state_count = fields.Int(metadata=get_json_metadata("The number of states"))


def get_change_field(field_name):
    return fields.Int(
        metadata=get_json_metadata(
            f"The change in {field_name} since the last notification"
        )
    )


def get_count_field(field_name):
    return fields.Int(metadata=get_json_metadata(f"The number of {field_name}"))


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


class MetricsFollowedSearchesBreakdownRequestSchema(Schema):
    page = PAGE_FIELD
    sort_by = get_sort_by_field(
        allowed_values=GET_METRICS_FOLLOWED_SEARCHES_BREAKDOWN_SORTABLE_COLUMNS
    )
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
