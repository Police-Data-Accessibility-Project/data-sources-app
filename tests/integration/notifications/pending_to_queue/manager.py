"""
Manager does the following:

- Creates two users with overlapping follows of the same given location
- Creates a data source and data request the events will be associated with
- Sets all 3 event types in the respective `Pending` tables`
- Checks for presence of events in the respective `Queue` tables
- Calls the `DatabaseClient.optionally_update_user_notification_queue` setting
"""

from sqlalchemy import delete

from db.enums import EventType
from db.models.implementations.core.notification.pending.data_request import (
    DataRequestPendingEventNotification,
)
from db.models.implementations.core.notification.pending.data_source import (
    DataSourcePendingEventNotification,
)
from tests.helper_scripts.helper_classes.test_data_creator.db_client_.core import (
    TestDataCreatorDBClient,
)


class NotificationsPendingToQueueTestManager:

    def __init__(self, tdc: TestDataCreatorDBClient):
        self.tdc = tdc
        self.db_client = tdc.db_client
        self.user_id_1 = self.tdc.user().id
        self.user_id_2 = self.tdc.user().id
        self.data_source_id = self.tdc.data_source().id
        self.data_request_id = self.tdc.data_request().id
        # Clear pending tables to ensure clean slate
        self._clear_pending_tables()

    def _clear_pending_tables(self):
        for model in [
            DataRequestPendingEventNotification,
            DataSourcePendingEventNotification,
        ]:
            query = delete(model)
            self.db_client.execute(query)

    def _setup_user_follows(self, location_id: int):
        # Link entities to location
        self.tdc.link_data_request_to_location(
            data_request_id=self.data_request_id, location_id=location_id
        )
        agency_id = self.tdc.agency(location_id=location_id).id
        self.tdc.link_data_source_to_agency(
            data_source_id=self.data_source_id, agency_id=agency_id
        )

        for user_id in [self.user_id_1, self.user_id_2]:
            self.tdc.user_follow_location(user_id=user_id, location_id=location_id)

    def _add_entries_to_pending(self):
        """Add relevant events for each entity to the respective `Pending` tables"""
        entries = [
            DataRequestPendingEventNotification(
                data_request_id=self.data_request_id,
                event_type=EventType.REQUEST_READY_TO_START.value,
            ),
            DataRequestPendingEventNotification(
                data_request_id=self.data_request_id,
                event_type=EventType.REQUEST_COMPLETE.value,
            ),
            DataSourcePendingEventNotification(
                data_source_id=self.data_source_id,
                event_type=EventType.DATA_SOURCE_APPROVED.value,
            ),
        ]
        self.tdc.db_client.add_many(entries)

    def setup(self, location_id: int) -> None:
        self._setup_user_follows(location_id=location_id)
        self._add_entries_to_pending()
