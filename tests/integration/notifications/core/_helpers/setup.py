from db.enums import EventType, EntityType
from tests.helper_scripts.helper_classes.test_data_creator.db_client_.core import (
    TestDataCreatorDBClient,
    ValidNotificationEventCreatorV2,
)
from tests.integration.notifications.core._helpers.expected_event_info import (
    ExpectedEventInfo,
)
from tests.integration.notifications.core._helpers.models.user import (
    NotificationsTestUserInfo,
)


class NotificationsTestSetupManager:
    def __init__(self, tdc: TestDataCreatorDBClient):
        self.tdc = tdc
        self.vnec = ValidNotificationEventCreatorV2(self.tdc)

    def _create_event(
        self, event_type: EventType, entity_type: EntityType, user_id: int
    ) -> ExpectedEventInfo:
        entity_id = self.tdc.create_valid_notification_event(
            event_type=event_type, user_id=user_id
        )
        return ExpectedEventInfo(
            event_type=event_type, entity_id=entity_id, entity_type=entity_type
        )

    def create_every_event_type_user(self) -> NotificationsTestUserInfo:
        """Create user with a general follow of every event type"""
        user_info = self.tdc.user()
        user_id = user_info.id
        user_email = user_info.email
        return NotificationsTestUserInfo(
            user_id=user_id,
            user_email=user_email,
            expected_events=[
                self._create_event(
                    EventType.REQUEST_READY_TO_START, EntityType.DATA_REQUEST, user_id
                ),
                self._create_event(
                    EventType.REQUEST_COMPLETE, EntityType.DATA_REQUEST, user_id
                ),
                self._create_event(
                    EventType.DATA_SOURCE_APPROVED, EntityType.DATA_SOURCE, user_id
                ),
            ],
        )

    def create_single_event_type_user(self) -> NotificationsTestUserInfo:
        """Create user with a general follow of a single event type"""
        user_info = self.tdc.user()
        user_id = user_info.id
        user_email = user_info.email
        return NotificationsTestUserInfo(
            user_id=user_id,
            user_email=user_email,
            expected_events=[
                self._create_event(
                    EventType.REQUEST_READY_TO_START, EntityType.DATA_REQUEST, user_id
                ),
            ],
        )

    def create_national_event_type_user(self) -> NotificationsTestUserInfo:
        """Create user that follows a national record type"""
        user_info = self.tdc.user()
        user_id = user_info.id
        user_email = user_info.email
        return NotificationsTestUserInfo(
            user_id=user_id,
            user_email=user_email,
            expected_events=[
                self._create_event(
                    EventType.DATA_SOURCE_APPROVED, EntityType.DATA_SOURCE, user_id
                ),
            ],
        )
