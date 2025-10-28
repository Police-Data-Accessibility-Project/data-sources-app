from tests.integration.notifications.pending_to_queue.location.manager import (
    NotificationsPendingToQueueLocationTestManager,
)


def test_notifications_pending_to_queue_indirect_follow_national_locality(
    national_id,
    pittsburgh_id,
    manager: NotificationsPendingToQueueLocationTestManager,
):
    manager.run(follow_location_id=national_id, entity_location_id=pittsburgh_id)
