"""
A 'direct' follow in this case refers to a location the user is following.
"""

from tests.integration.notifications.pending_to_queue.manager import (
    NotificationsPendingToQueueTestManager,
)


def test_notifications_pending_to_queue_direct_follow(
    manager: NotificationsPendingToQueueTestManager, pittsburgh_id
):
    manager.run(follow_location_id=pittsburgh_id, entity_location_id=pittsburgh_id)
