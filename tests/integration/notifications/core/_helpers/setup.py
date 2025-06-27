from db.enums import EventType, EntityType
from tests.helper_scripts.helper_classes.test_data_creator.db_client_.core import (
    TestDataCreatorDBClient,
    ValidNotificationEventCreatorV2,
)
from tests.integration.notifications.core._helpers.expected_event_info import (
    ExpectedEventInfo,
)
from tests.integration.notifications.core._helpers.models.entity_setup import (
    EntitySetupInfo,
)
from tests.integration.notifications.core._helpers.models.user import (
    NotificationsTestUserInfo,
)


class NotificationsTestSetupManager:

    def __init__(self, tdc: TestDataCreatorDBClient):
        self.tdc = tdc
        self.vnec = ValidNotificationEventCreatorV2(self.tdc)

    def setup_entities(self, entity_setup_info: list[EntitySetupInfo]):
        for entity_setup in entity_setup_info:
            self._setup_entity(entity_setup)

    def _setup_entity(self, entity_setup: EntitySetupInfo):
        if entity_setup.event_set_info.entity_type == EntityType.DATA_REQUEST:
            self._handle_data_request_event(entity_setup)
        elif entity_setup.event_set_info.entity_type == EntityType.DATA_SOURCE:
            self._handle_data_source_event(entity_setup)

    def _handle_data_request_event(self, entity_setup: EntitySetupInfo):
        """Sets up data request entity and updates entity setup info in-place."""
        set_info = entity_setup.event_set_info
        if set_info.has_event_type(EventType.REQUEST_READY_TO_START):
            raise NotImplementedError
        if set_info.has_event_type(EventType.REQUEST_COMPLETE):
            raise NotImplementedError

    def _handle_data_source_event(self, entity_setup: EntitySetupInfo) -> None:
        """Sets up data source entity and updates entity setup info in-place."""
        entity_setup.entity_id = self.vnec.data_source_approved(
            record_type=entity_setup.record_type,
            location_id=entity_setup.location_id,
        )

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
