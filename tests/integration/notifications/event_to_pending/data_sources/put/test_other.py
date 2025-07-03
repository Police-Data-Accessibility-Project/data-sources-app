"""
When a data source is updated to any status other than approved,
the relevant event should not be added to the notification queue
"""

from db.enums import ApprovalStatus
from tests.integration.notifications.event_to_pending.data_sources.put.manager import (
    EventToPendingDataSourcesPutTestManager,
)


def test_data_source_put_approved(manager: EventToPendingDataSourcesPutTestManager):
    for status in [s for s in ApprovalStatus if s != ApprovalStatus.APPROVED]:
        manager.update_approval_status(status)
        # Should not be in queue
        assert not manager._is_in_pending()
