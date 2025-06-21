# pyright: reportUninitializedInstanceVariable=false
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.mixins import UserIDMixin
from db.models.templates.standard import StandardBase
from db.models.types import timestamp
from middleware.enums import Relations


class DataRequestUserNotificationQueue(StandardBase, UserIDMixin):
    __tablename__ = Relations.DATA_REQUESTS_USER_NOTIFICATION_QUEUE.value

    event_id: Mapped[int] = mapped_column(
        ForeignKey("public.data_request_pending_event_notification.id")
    )
    sent_at: Mapped[Optional[timestamp]]

    # Relationships
    pending_event_notification = relationship(
        argument="DataRequestPendingEventNotification",
        primaryjoin="DataRequestUserNotificationQueue.event_id == DataRequestPendingEventNotification.id",
        uselist=False,
    )
