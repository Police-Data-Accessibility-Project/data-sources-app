from db.enums import EventType, EntityType
from db.dtos.event_batch import EventBatch
from db.dtos.event_info import EventInfo
from middleware.primary_resource_logic.notifications.notifications import (
    format_and_send_notifications,
)
from middleware.util.env import get_env_variable


def test_notifications_email():
    event_batch = EventBatch(
        user_id=1,
        user_email=get_env_variable("TEST_EMAIL_ADDRESS"),
        events=[
            EventInfo(
                event_id=1,
                event_type=EventType.DATA_SOURCE_APPROVED,
                entity_id=1,
                entity_type=EntityType.DATA_SOURCE,
                entity_name="Test Data Source",
            ),
            EventInfo(
                event_id=2,
                event_type=EventType.DATA_SOURCE_APPROVED,
                entity_id=2,
                entity_type=EntityType.DATA_SOURCE,
                entity_name="Test Data Source 2",
            ),
            EventInfo(
                event_id=3,
                event_type=EventType.REQUEST_COMPLETE,
                entity_id=3,
                entity_type=EntityType.DATA_REQUEST,
                entity_name="Test Data Request 3",
            ),
            EventInfo(
                event_id=4,
                event_type=EventType.REQUEST_READY_TO_START,
                entity_id=4,
                entity_type=EntityType.DATA_REQUEST,
                entity_name="Test Data Request 4",
            ),
        ],
    )
    format_and_send_notifications(event_batch=event_batch)
