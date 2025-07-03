"""
When data requests are marked as completed,
the relevant event is added to the notification queue
with the proper attributes
"""

from db.enums import RequestStatus
from tests.integration.notifications.event_to_pending.data_requests.manager import (
    EventToPendingDataRequestsTestManager,
)


def test_data_requests_added_to_queue_complete(
    manager: EventToPendingDataRequestsTestManager,
):
    manager.update_request_status(request_status=RequestStatus.COMPLETE)
    # Should be in queue
    assert manager.is_in_pending()
