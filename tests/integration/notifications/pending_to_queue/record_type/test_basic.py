from tests.integration.notifications.pending_to_queue.location.manager import (
    NotificationsPendingToQueueLocationTestManager,
)


# TODO: Broken by other changes and not being isolated by other tests. Fix.
# def test_notifications_pending_to_queue_record_type_direct_follow(
#     manager: NotificationsPendingToQueueLocationTestManager,
#     pittsburgh_id,
# ):
#     manager.run(
#         follow_location_id=pittsburgh_id,
#         entity_location_id=pittsburgh_id
#     )
