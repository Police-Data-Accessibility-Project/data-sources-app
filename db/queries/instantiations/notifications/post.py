from typing import Optional

from sqlalchemy import select, or_, exists, and_
from sqlalchemy.orm import selectinload

from db.enums import EventType, EntityType
from db.models.implementations.core.notification.queue.data_request import (
    DataRequestUserNotificationQueue,
)
from db.models.implementations.core.notification.queue.data_source import (
    DataSourceUserNotificationQueue,
)
from db.models.implementations.core.user.core import User
from db.queries.builder_.core import QueryBuilderBase
from middleware.custom_dataclasses import EventBatch, EventInfo


class NotificationsPostQueryBuilder(QueryBuilderBase):

    def run(self) -> Optional[EventBatch]:
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
            .limit(1)
        )

        raw_results = self.session.execute(query).first()
        if raw_results is None:
            return None
        user = raw_results[0]
        event_infos = []
        for event in user.data_request_events:
            event_info = EventInfo(
                event_id=event.id,
                event_type=EventType(event.event_type),
                entity_id=event.data_request.id,
                entity_type=EntityType.DATA_REQUEST,
                entity_name=event.data_request.title,
            )
            event_infos.append(event_info)
        for event in user.data_source_events:
            event_info = EventInfo(
                event_id=event.id,
                event_type=EventType(event.event_type),
                entity_id=event.data_source.id,
                entity_type=EntityType.DATA_SOURCE,
                entity_name=event.data_source.name,
            )
            event_infos.append(event_info)
        return EventBatch(user_id=user.id, user_email=user.email, events=event_infos)
