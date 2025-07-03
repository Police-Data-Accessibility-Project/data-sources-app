from pydantic import BaseModel

from db.enums import EventType


class CheckInfo(BaseModel):
    entity_id: int
    event_type: EventType
    user_id: int
