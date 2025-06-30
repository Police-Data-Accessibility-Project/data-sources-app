import pytest

from tests.integration.notifications.event_to_pending.data_sources.put.manager import (
    EventToPendingDataSourcesPutTestManager,
)


@pytest.fixture
def manager(test_data_creator_db_client) -> EventToPendingDataSourcesPutTestManager:
    manager = EventToPendingDataSourcesPutTestManager(test_data_creator_db_client)
    return manager
