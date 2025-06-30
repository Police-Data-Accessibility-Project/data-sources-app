from typing import final

from marshmallow import Schema

from middleware.schema_and_dto.schemas.helpers import int_field, date_field


@final
class MetricsFollowedSearchesAggregateResponseSchema(Schema):
    total_followers = int_field("The total number of followers")
    total_followed_searches = int_field("The total number of followed searches")
    last_notification_date = date_field(
        "The date that notifications were sent out",
        allow_none=True,
    )
