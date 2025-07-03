"""
When data requests are marked as ready to start,
the relevant event is added to the notification queue
with the proper attributes
"""

from db.enums import RequestStatus
from tests.integration.notifications.event_to_pending.data_requests.manager import (
    EventToPendingDataRequestsTestManager,
)


def test_data_requests_added_to_queue_ready_to_start(
    manager: EventToPendingDataRequestsTestManager,
):
    manager.update_request_status(request_status=RequestStatus.READY_TO_START)
    # Should be in queue
    assert manager.is_in_pending()
