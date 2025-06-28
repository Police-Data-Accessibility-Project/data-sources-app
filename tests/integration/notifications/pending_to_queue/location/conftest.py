import pytest

from tests.integration.notifications.pending_to_queue.location.manager import (
    NotificationsPendingToQueueLocationTestManager,
)


@pytest.fixture
def manager(test_data_creator_db_client) -> NotificationsPendingToQueueLocationTestManager:
    manager = NotificationsPendingToQueueLocationTestManager(test_data_creator_db_client)
    return manager
