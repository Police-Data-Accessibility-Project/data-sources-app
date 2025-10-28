"""
A 'direct' follow in this case refers to a location the user is following.
"""

from tests.integration.notifications.pending_to_queue.location.manager import (
    NotificationsPendingToQueueLocationTestManager,
)


def test_notifications_pending_to_queue_direct_follow(
    pittsburgh_id: int,
    manager: NotificationsPendingToQueueLocationTestManager
):
    manager.run(follow_location_id=pittsburgh_id, entity_location_id=pittsburgh_id)
