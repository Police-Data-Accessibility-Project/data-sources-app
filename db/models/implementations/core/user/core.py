# pyright: reportUninitializedInstanceVariable=false
from typing import Optional

from sqlalchemy import text as text_func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.mixins import CreatedAtMixin
from db.models.templates.standard import StandardBase
from db.models.types import timestamp_tz, text
from middleware.enums import Relations


class User(StandardBase, CreatedAtMixin):
    __tablename__ = Relations.USERS.value

    updated_at: Mapped[timestamp_tz | None]
    email: Mapped[str] = mapped_column(unique=True)
    password_digest: Mapped[str | None]
    api_key: Mapped[str | None] = mapped_column(
        server_default=text_func("generate_api_key()")
    )
    role: Mapped[text | None]

    # Relationships
    created_agencies = relationship(
        argument="Agency",
        back_populates="creator",
    )
    permissions = relationship(
        argument="Permission",
        secondary="public.user_permissions",
        primaryjoin="User.id == UserPermission.user_id",
        secondaryjoin="UserPermission.permission_id == Permission.id",
    )
    data_request_events = relationship(
        argument="DataRequestPendingEventNotification",
        secondary="public.data_request_user_notification_queue",
        primaryjoin="User.id == DataRequestUserNotificationQueue.user_id",
        secondaryjoin="DataRequestUserNotificationQueue.event_id == DataRequestPendingEventNotification.id",
        order_by="DataRequestUserNotificationQueue.id",
    )
    data_source_events = relationship(
        argument="DataSourcePendingEventNotification",
        secondary="public.data_source_user_notification_queue",
        primaryjoin="User.id == DataSourceUserNotificationQueue.user_id",
        secondaryjoin="DataSourceUserNotificationQueue.event_id == DataSourcePendingEventNotification.id",
        order_by="DataSourceUserNotificationQueue.id",
    )
