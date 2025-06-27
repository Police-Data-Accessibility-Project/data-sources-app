"""
When a data source is updated to approved,
the relevant event is added to the notification queue
with the proper attributes
"""

from db.enums import ApprovalStatus
from tests.integration.notifications.event_to_pending.data_sources.put.manager import (
    EventToPendingDataSourcesPutTestManager,
)


def test_data_source_put_approved(manager: EventToPendingDataSourcesPutTestManager):
    manager.update_approval_status(ApprovalStatus.APPROVED)
    # Should be in queue
    assert manager._is_in_pending()
