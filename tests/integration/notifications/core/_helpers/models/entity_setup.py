from pydantic import BaseModel

from middleware.enums import RecordTypes
from tests.integration.notifications.core._helpers.models.event_set import EventSetInfo


class EntitySetupInfo(BaseModel):
    location_id: int
    record_type: RecordTypes
    event_set_info: EventSetInfo
    entity_id: int | None = None
