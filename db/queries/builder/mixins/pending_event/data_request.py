from db.enums import EventType
from db.models.implementations.core.notification.pending.data_request import (
    DataRequestPendingEventNotification,
)
from db.queries.builder.core import QueryBuilderBase


class DataRequestPendingEventMixin:

    def _add_pending_event_notification(
        self: QueryBuilderBase, data_request_id: int, event_type: EventType
    ):
        pending_event_notification = DataRequestPendingEventNotification(
            data_request_id=data_request_id,
            event_type=event_type.value,
        )
        self.session.add(pending_event_notification)
