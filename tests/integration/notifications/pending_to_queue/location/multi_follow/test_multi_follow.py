from tests.helpers.helper_classes.test_data_creator.db_client_.core import (
    TestDataCreatorDBClient,
)
from tests.integration.notifications.pending_to_queue.location.manager import (
    NotificationsPendingToQueueLocationTestManager,
)


def test_notifications_pending_to_queue_multi_follow(
    pittsburgh_id,
    allegheny_id,
    test_data_creator_db_client: TestDataCreatorDBClient,
    manager: NotificationsPendingToQueueLocationTestManager,
):
    manager.setup_follow_locations(
        follow_location_ids=[pittsburgh_id, allegheny_id],
        entity_location_id=pittsburgh_id,
    )
    manager.check_results()
