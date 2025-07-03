"""
When a data source is created with any status other than approved,
the relevant event should not be added to the notification queue
"""

from db.enums import ApprovalStatus
from tests.integration.notifications.event_to_pending.data_sources.manager import (
    EventToPendingDataSourcesTestManager,
)


def test_data_source_post_other(manager: EventToPendingDataSourcesTestManager):
    for status in [s for s in ApprovalStatus if s != ApprovalStatus.APPROVED]:
        id_ = manager.tdc.data_source(status).id
        # Should not be in queue
        assert not manager.is_in_pending(id_)
