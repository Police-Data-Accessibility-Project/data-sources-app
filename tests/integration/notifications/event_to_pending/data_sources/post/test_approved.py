"""
When a data source is created and approved,
the relevant event is added to the notification queue
with the proper attributes
"""

from db.enums import ApprovalStatus
from tests.integration.notifications.event_to_pending.data_sources.manager import (
    EventToPendingDataSourcesTestManager,
)


def test_data_source_post_approved(manager: EventToPendingDataSourcesTestManager):
    id_ = manager.tdc.data_source(ApprovalStatus.APPROVED).id
    # Should be in queue
    assert manager.is_in_pending(id_)
