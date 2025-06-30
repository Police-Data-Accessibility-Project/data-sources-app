import pytest

from tests.integration.notifications.event_to_pending.data_requests.manager import (
    EventToPendingDataRequestsTestManager,
)


@pytest.fixture
def manager(test_data_creator_db_client) -> EventToPendingDataRequestsTestManager:
    manager = EventToPendingDataRequestsTestManager(test_data_creator_db_client)
    return manager
