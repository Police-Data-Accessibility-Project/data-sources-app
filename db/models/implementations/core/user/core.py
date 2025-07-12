# pyright: reportUninitializedInstanceVariable=false
from typing import final

from sqlalchemy import text as text_func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.mixins import CreatedAtMixin
from db.models.templates.standard import StandardBase
from db.models.types import timestamp_tz, text
from middleware.enums import Relations

@final
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
    data_requests = relationship(
        argument="DataRequest",
        primaryjoin="User.id == DataRequest.creator_user_id",
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
    followed_locations = relationship(
        argument="Location",
        secondary="public.link_user_followed_location",
        primaryjoin="User.id == LinkUserFollowedLocation.user_id",
        secondaryjoin="LinkUserFollowedLocation.location_id == Location.id",
    )
    follows = relationship(
        argument="LinkUserFollowedLocation",
    )
    recent_searches = relationship(
        argument="RecentSearch",
        back_populates="user",
    )
    external_accounts = relationship(
        argument="ExternalAccount",
        back_populates="user",
    )
    capacities = relationship(
        argument="UserCapacity",
        back_populates="user",
    )
