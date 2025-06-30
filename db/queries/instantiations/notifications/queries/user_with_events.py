from sqlalchemy import select, or_, exists, and_, Select
from sqlalchemy.orm import selectinload

from db.models.implementations.core.notification.queue.data_request import (
    DataRequestUserNotificationQueue,
)
from db.models.implementations.core.notification.queue.data_source import (
    DataSourceUserNotificationQueue,
)
from db.models.implementations.core.user.core import User


def get_user_with_events_query() -> Select[tuple[User]]:
    query = (
        select(User)
        .where(
            or_(
                exists(
                    select(DataSourceUserNotificationQueue.id).where(
                        and_(
                            DataSourceUserNotificationQueue.user_id == User.id,
                            DataSourceUserNotificationQueue.sent_at.is_(None),
                        )
                    )
                ),
                exists(
                    select(DataRequestUserNotificationQueue.id).where(
                        and_(
                            DataRequestUserNotificationQueue.user_id == User.id,
                            DataRequestUserNotificationQueue.sent_at.is_(None),
                        )
                    )
                ),
            )
        )
        .options(
            selectinload(User.data_request_events),
            selectinload(User.data_source_events),
        )
    )
    return query
