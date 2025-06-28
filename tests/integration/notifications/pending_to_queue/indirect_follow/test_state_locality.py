from tests.integration.notifications.pending_to_queue.manager import (
    NotificationsPendingToQueueTestManager,
)


def test_notifications_pending_to_queue_indirect_follow_state_locality(
    manager: NotificationsPendingToQueueTestManager, pennsylvania_id, pittsburgh_id
):
    manager.run(follow_location_id=pennsylvania_id, entity_location_id=pittsburgh_id)
