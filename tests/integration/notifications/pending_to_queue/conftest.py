import pytest

from tests.integration.notifications.pending_to_queue.manager import (
    NotificationsPendingToQueueTestManager,
)


@pytest.fixture
def manager(test_data_creator_db_client) -> NotificationsPendingToQueueTestManager:
    manager = NotificationsPendingToQueueTestManager(test_data_creator_db_client)
    return manager
