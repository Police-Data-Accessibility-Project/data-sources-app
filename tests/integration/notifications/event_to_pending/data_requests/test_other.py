"""
Modifying data requests to any other request status
should not result in an event being added to the notification queue.
"""

from db.enums import RequestStatus
from tests.integration.notifications.event_to_pending.data_requests.manager import (
    EventToPendingDataRequestsTestManager,
)


def test_data_requests_added_to_queue_irrelevant_status(
    manager: EventToPendingDataRequestsTestManager,
):
    for request_status in RequestStatus:
        if request_status == RequestStatus.COMPLETE:
            continue
        if request_status == RequestStatus.READY_TO_START:
            continue
        manager.update_request_status(request_status=request_status)
        # Should not be in queue
        assert not manager.is_in_pending()
