from tests.integration.notifications.pending_to_queue.location.manager import (
    NotificationsPendingToQueueLocationTestManager,
)


def test_notifications_pending_to_queue_indirect_follow_state_county(
    manager: NotificationsPendingToQueueLocationTestManager,
    pennsylvania_id,
    allegheny_id,
):
    manager.run(follow_location_id=pennsylvania_id, entity_location_id=allegheny_id)
