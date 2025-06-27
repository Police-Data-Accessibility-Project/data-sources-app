import pytest

from tests.integration.notifications.event_to_pending.data_sources.manager import (
    EventToPendingDataSourcesTestManager,
)


@pytest.fixture
def manager(test_data_creator_db_client) -> EventToPendingDataSourcesTestManager:
    manager = EventToPendingDataSourcesTestManager(test_data_creator_db_client)
    return manager
