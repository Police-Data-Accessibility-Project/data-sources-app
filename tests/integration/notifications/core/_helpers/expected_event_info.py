from pydantic import BaseModel

from db.enums import EventType, EntityType


class ExpectedEventInfo(BaseModel):
    event_type: EventType
    entity_type: EntityType
    entity_id: int
