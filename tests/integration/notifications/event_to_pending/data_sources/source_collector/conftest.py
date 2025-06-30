import pytest

from tests.integration.notifications.event_to_pending.data_sources.source_collector.manager import (
    EventToPendingDataSourcesSourceCollectorTestManager,
)


@pytest.fixture
def manager(
    test_data_creator_db_client,
) -> EventToPendingDataSourcesSourceCollectorTestManager:
    return EventToPendingDataSourcesSourceCollectorTestManager(
        test_data_creator_db_client
    )
