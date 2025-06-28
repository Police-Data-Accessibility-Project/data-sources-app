import pytest

from tests.integration.notifications.pending_to_queue.record_type.manager import (
    NotificationsPendingToQueueRecordTypeTestManager,
)


@pytest.fixture
def manager(
    test_data_creator_db_client,
) -> NotificationsPendingToQueueRecordTypeTestManager:
    return NotificationsPendingToQueueRecordTypeTestManager(test_data_creator_db_client)
