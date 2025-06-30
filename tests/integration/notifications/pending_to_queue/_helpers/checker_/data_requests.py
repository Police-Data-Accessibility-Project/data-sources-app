from typing import override

from sqlalchemy import select

from db.models.implementations.core.notification.pending.data_request import (
    DataRequestPendingEventNotification,
)
from db.models.implementations.core.notification.queue.data_request import (
    DataRequestUserNotificationQueue,
)
from tests.integration.notifications.pending_to_queue._helpers.check_info import (
    CheckInfo,
)
from tests.integration.notifications.pending_to_queue._helpers.checker_._base import (
    EventQueueCheckerBase,
)


class DataRequestsEventQueueChecker(EventQueueCheckerBase):
    @override
    def _get_notification_queue_check_infos(self) -> list[CheckInfo]:
        query = select(
            DataRequestUserNotificationQueue.user_id,
            DataRequestPendingEventNotification.data_request_id.label("entity_id"),
            DataRequestPendingEventNotification.event_type.label("event_type"),
        ).join(
            DataRequestPendingEventNotification,
            DataRequestUserNotificationQueue.event_id
            == DataRequestPendingEventNotification.id,
        )
        return self._process_query(query)
