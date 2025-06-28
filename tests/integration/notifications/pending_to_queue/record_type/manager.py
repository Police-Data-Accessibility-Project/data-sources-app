from sqlalchemy import delete, select
from sqlalchemy.sql.functions import count

from db.enums import EventType
from db.models.implementations.core.notification.pending.data_request import DataRequestPendingEventNotification
from db.models.implementations.core.notification.pending.data_source import DataSourcePendingEventNotification
from db.models.implementations.core.notification.queue.data_request import DataRequestUserNotificationQueue
from db.models.implementations.core.notification.queue.data_source import DataSourceUserNotificationQueue
from middleware.enums import RecordTypes
from tests.helper_scripts.helper_classes.test_data_creator.db_client_.core import (
    TestDataCreatorDBClient,
)
from tests.integration.notifications.pending_to_queue._helpers.checker_.data_requests import \
    DataRequestsEventQueueChecker
from tests.integration.notifications.pending_to_queue._helpers.checker_.data_sources import DataSourcesEventQueueChecker


class NotificationsPendingToQueueRecordTypeTestManager:

    def __init__(self, tdc: TestDataCreatorDBClient):
        self.tdc = tdc
        self.tdc.clear_test_data()
        self.db_client = tdc.db_client
        self.user_id_1 = self.tdc.user().id
        self.user_id_2 = self.tdc.user().id

        self.data_source_accident_id = self.tdc.data_source(
            record_type=RecordTypes.ACCIDENT_REPORTS
        ).id
        self.data_request_accident_id = self.tdc.data_request(
            record_type=RecordTypes.ACCIDENT_REPORTS
        ).id
        self.data_source_court_id = self.tdc.data_source(
            record_type=RecordTypes.COURT_CASES
        ).id
        self.data_request_court_id = self.tdc.data_request(
            record_type=RecordTypes.COURT_CASES
        ).id

        # Clear pending tables to ensure clean slate
        self._clear_pending_tables()
        self.dr_checker: DataRequestsEventQueueChecker | None = None
        self.ds_checker: DataSourcesEventQueueChecker | None = None

    def get_data_request_ids(self) -> list[int]:
        return [
            self.data_request_accident_id,
            self.data_request_court_id
        ]

    def get_data_source_ids(self) -> list[int]:
        return [
            self.data_source_accident_id,
            self.data_source_court_id
        ]

    def _clear_pending_tables(self):
        for model in [
            DataRequestPendingEventNotification,
            DataSourcePendingEventNotification,
        ]:
            query = delete(model)
            self.db_client.execute(query)

    def _setup_entity_location(self, location_id: int):
        for dr_id in self.get_data_request_ids():
            self.tdc.link_data_request_to_location(
                data_request_id=dr_id, location_id=location_id
            )
        for ds_id in self.get_data_source_ids():
            agency_id = self.tdc.agency(location_id=location_id).id
            self.tdc.link_data_source_to_agency(
                data_source_id=ds_id, agency_id=agency_id
            )

    def _add_entries_to_pending(self):
        """Add relevant events for each entity to the respective `Pending` tables"""
        entries = []
        for dr_id in self.get_data_request_ids():
            entries.append(
                DataRequestPendingEventNotification(
                    data_request_id=dr_id,
                    event_type=EventType.REQUEST_READY_TO_START.value,
                )
            )
            entries.append(
                DataRequestPendingEventNotification(
                    data_request_id=dr_id,
                    event_type=EventType.REQUEST_COMPLETE.value,
                )
            )
        for ds_id in self.get_data_source_ids():
            entries.append(
                DataSourcePendingEventNotification(
                    data_source_id=ds_id,
                    event_type=EventType.DATA_SOURCE_APPROVED.value,
                )
            )
        self.tdc.db_client.add_many(entries)

    def _setup_user_follows(self, location_id: int):
        # User 1 follows a location without specifying record type
        self.tdc.user_follow_location(user_id=self.user_id_1, location_id=location_id)
        # User 2 follows a location with a specific record type
        self.tdc.user_follow_location(
            user_id=self.user_id_2,
            location_id=location_id,
            record_types=[RecordTypes.ACCIDENT_REPORTS],
        )

    def _check_for_all_data_request_events(self, user_id: int):
        for dr_id in self.get_data_request_ids():
            assert self.dr_checker.user_has_event(
                user_id=user_id,
                entity_id=dr_id,
                event_type=EventType.REQUEST_READY_TO_START,
            )
            assert self.dr_checker.user_has_event(
                user_id=user_id,
                entity_id=dr_id,
                event_type=EventType.REQUEST_COMPLETE,
            )

    def _check_results_for_users(self):
        # User 1
        self._check_for_all_data_request_events(self.user_id_1)
        for ds_id in self.get_data_source_ids():
            assert self.ds_checker.user_has_event(
                user_id=self.user_id_1,
                entity_id=ds_id,
                event_type=EventType.DATA_SOURCE_APPROVED,
            )

        # User 2
        self._check_for_all_data_request_events(self.user_id_2)
        assert self.ds_checker.user_has_event(
            user_id=self.user_id_2,
            entity_id=self.data_source_accident_id,
            event_type=EventType.DATA_SOURCE_APPROVED,
        )
        assert not self.ds_checker.user_has_event(
            user_id=self.user_id_2,
            entity_id=self.data_source_court_id,
            event_type=EventType.DATA_SOURCE_APPROVED,
        )


    def setup(self, follow_location_id: int, entity_location_id: int) -> None:
        self._setup_user_follows(location_id=follow_location_id)
        self._setup_entity_location(location_id=entity_location_id)
        self._add_entries_to_pending()
        self.db_client.optionally_update_user_notification_queue()
        self.dr_checker = DataRequestsEventQueueChecker(self.db_client)
        self.ds_checker = DataSourcesEventQueueChecker(self.db_client)


    def run(self, follow_location_id: int, entity_location_id: int):
        self.setup(
            follow_location_id=follow_location_id, entity_location_id=entity_location_id
        )
        self.check_results()

    def check_results(self):
        self._check_results_for_users()
        self.check_expected_queue_count(
            dr_count_expected=8,
            ds_count_expected=3
        )

    def check_expected_queue_count(
        self, dr_count_expected: int, ds_count_expected: int
    ):
        dr_query = select(count(DataRequestUserNotificationQueue.id))
        ds_query = select(count(DataSourceUserNotificationQueue.id))
        dr_count_actual = self.db_client.scalar(dr_query)
        ds_count_actual = self.db_client.scalar(ds_query)
        assert (
            dr_count_actual == dr_count_expected
        ), f"Expected {dr_count_expected} but got {dr_count_actual}"
        assert (
            ds_count_actual == ds_count_expected
        ), f"Expected {ds_count_expected} but got {ds_count_actual}"
