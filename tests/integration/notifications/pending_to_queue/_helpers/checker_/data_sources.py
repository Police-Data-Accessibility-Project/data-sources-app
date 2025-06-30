from typing import override

from sqlalchemy import select

from db.models.implementations.core.notification.pending.data_source import (
    DataSourcePendingEventNotification,
)
from db.models.implementations.core.notification.queue.data_source import (
    DataSourceUserNotificationQueue,
)
from tests.integration.notifications.pending_to_queue._helpers.check_info import (
    CheckInfo,
)
from tests.integration.notifications.pending_to_queue._helpers.checker_._base import (
    EventQueueCheckerBase,
)


class DataSourcesEventQueueChecker(EventQueueCheckerBase):
    @override
    def _get_notification_queue_check_infos(self) -> list[CheckInfo]:
        query = select(
            DataSourceUserNotificationQueue.user_id,
            DataSourcePendingEventNotification.data_source_id.label("entity_id"),
            DataSourcePendingEventNotification.event_type.label("event_type"),
        ).join(
            DataSourcePendingEventNotification,
            DataSourceUserNotificationQueue.event_id
            == DataSourcePendingEventNotification.id,
        )
        return self._process_query(query)
