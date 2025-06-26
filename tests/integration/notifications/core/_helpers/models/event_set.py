from pydantic import BaseModel

from db.enums import EntityType, EventType


class EventSetInfo(BaseModel):
    entity_type: EntityType
    event_types: list[EventType]

    def has_event_type(self, event_type: EventType):
        return event_type in self.event_types
