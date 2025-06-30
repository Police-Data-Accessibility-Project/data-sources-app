from db.enums import EventType
from db.models.implementations.core.notification.pending.data_source import (
    DataSourcePendingEventNotification,
)
from db.queries.builder.core import QueryBuilderBase


class DataSourcePendingEventMixin:
    def _add_pending_event_notification(
        self: QueryBuilderBase, data_source_id: int
    ) -> None:
        pending_event_notification = DataSourcePendingEventNotification(
            data_source_id=data_source_id,
            event_type=EventType.DATA_SOURCE_APPROVED.value,  # pyright: ignore [reportUnknownMemberType]
        )
        self.session.add(pending_event_notification)
