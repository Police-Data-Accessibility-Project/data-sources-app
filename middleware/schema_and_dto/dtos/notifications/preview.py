from pydantic import BaseModel

from db.dtos.event_batch import EventBatch
from middleware.schema_and_dto.dtos._helpers import default_field_required


class NotificationsPreviewCount(BaseModel):
    total_events: int = default_field_required(
        description="The total number of events that will be sent.",
    )
    total_users: int = default_field_required(
        description="The total number of users that will be sent to.",
    )
    distinct_events: int = default_field_required(
        description="The total number of distinct events that will be sent.",
    )
    distinct_data_request_events: int = default_field_required(
        description="The total number of distinct data request events that will be sent.",
    )
    distinct_data_source_events: int = default_field_required(
        description="The total number of distinct data source events that will be sent.",
    )


class NotificationsPreviewOutput(BaseModel):
    counts: NotificationsPreviewCount = default_field_required(
        description="Various counts of events that will be sent.",
    )
    batches: list[EventBatch] = default_field_required(
        description="The batches of events that will be sent.",
    )
