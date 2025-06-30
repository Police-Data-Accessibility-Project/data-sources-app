# pyright: reportUnknownVariableType=false
from pydantic import BaseModel

from db.enums import EventType, EntityType
from middleware.schema_and_dto.dtos._helpers import default_field_required


class EventInfo(BaseModel):
    """
    Information about an event
    """

    event_id: int = default_field_required(
        description="The ID of the event (note: there are different IDs for different entity types)",
    )
    event_type: EventType = default_field_required(
        description="The type of event",
    )
    entity_id: int = default_field_required(
        description="The ID of the entity (note: there are different IDs for different entity types)",
    )
    entity_type: EntityType = default_field_required(
        description="The type of entity",
    )
    entity_name: str = default_field_required(
        description="The name of the entity",
    )
