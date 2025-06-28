from tests.integration.notifications.pending_to_queue.manager import (
    NotificationsPendingToQueueTestManager,
)


def test_notifications_pending_to_queue_indirect_follow_national_state(
    manager: NotificationsPendingToQueueTestManager,
    national_id,
    pennsylvania_id,
):
    manager.run(follow_location_id=national_id, entity_location_id=pennsylvania_id)
