from sqlalchemy import select

from db.client.core import DatabaseClient
from db.models.implementations.core.data_source.core import DataSource
from db.models.implementations.core.notification.pending.data_source import (
    DataSourcePendingEventNotification,
)
from tests.helper_scripts.helper_classes.test_data_creator.db_client_.core import (
    TestDataCreatorDBClient,
)
from tests.integration.notifications.event_to_pending.data_sources.manager import (
    EventToPendingDataSourcesTestManager,
)


class EventToPendingDataSourcesSourceCollectorTestManager:
    def __init__(self, tdc: TestDataCreatorDBClient):
        self.tdc = tdc
        self.tdc.clear_test_data()
        self.db_client: DatabaseClient = tdc.db_client
        self.inner_manager = EventToPendingDataSourcesTestManager(tdc)
        self.all_data_sources_in_queue(0)

    def _get_data_source_ids(self) -> list[int]:
        query = select(DataSource.id)
        results = self.tdc.db_client.scalars(query)
        return results

    def _get_queue_entity_ids(self) -> list[int]:
        query = select(DataSourcePendingEventNotification.data_source_id)
        results = self.tdc.db_client.scalars(query)
        return results

    def all_data_sources_in_queue(self, length: int):
        data_source_ids = self._get_data_source_ids()
        queue_entity_ids = self._get_queue_entity_ids()

        assert set(data_source_ids) == set(
            queue_entity_ids
        ), f"Data source/queue entity ids do not match: {data_source_ids} != {queue_entity_ids}"
        assert len(queue_entity_ids) == length
