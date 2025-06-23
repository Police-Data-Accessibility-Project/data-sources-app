# pyright: reportUninitializedInstanceVariable=false
from typing import Optional

from sqlalchemy import (
    ForeignKey,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from db.models.mixins import (
    UserIDMixin,
)
from db.models.templates.standard import StandardBase
from db.models.types import (
    timestamp,
)
from middleware.enums import Relations


class DataSourceUserNotificationQueue(StandardBase, UserIDMixin):
    __tablename__ = Relations.DATA_SOURCES_USER_NOTIFICATION_QUEUE.value

    event_id: Mapped[int] = mapped_column(
        ForeignKey("public.data_source_pending_event_notification.id")
    )
    sent_at: Mapped[Optional[timestamp]]

    # Relationships
    pending_event_notification = relationship(
        argument="DataSourcePendingEventNotification",
        primaryjoin="DataSourceUserNotificationQueue.event_id == DataSourcePendingEventNotification.id",
        uselist=False,
    )
