from pydantic import BaseModel

from db.dtos.event_info import EventInfo
from db.enums import EventType
from middleware.schema_and_dto.dtos._helpers import default_field_required


class EventBatch(BaseModel):
    """
    A batch of events
    """

    user_id: int = default_field_required(
        description="The ID of the user",
    )
    user_email: str = default_field_required(
        description="The email of the user",
    )
    events: list[EventInfo] = default_field_required(
        description="The events included in the batch",
    )

    def get_events_of_type(self, event_type: EventType):
        return [event for event in self.events if event.event_type == event_type]
