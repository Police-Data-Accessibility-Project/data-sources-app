from tests.integration.notifications.pending_to_queue.location.manager import (
    NotificationsPendingToQueueLocationTestManager,
)


def test_notifications_pending_to_queue_indirect_follow_national_county(
    manager: NotificationsPendingToQueueLocationTestManager,
    national_id,
    allegheny_id,
):
    manager.run(follow_location_id=national_id, entity_location_id=allegheny_id)
