from marshmallow import Schema, fields

from middleware.schema_and_dto.util import get_json_metadata


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
