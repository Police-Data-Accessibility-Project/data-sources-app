from typing import override

from db.enums import EventType, EntityType
from db.models.implementations.core.user.core import User
from db.queries.builder.core import QueryBuilderBase
from db.queries.instantiations.notifications.queries.user_with_events import (
    get_user_with_events_query,
)
from db.dtos.event_batch import EventBatch
from db.dtos.event_info import EventInfo


class NotificationsPostQueryBuilder(QueryBuilderBase):
    @override
    def run(self) -> EventBatch | None:
        query = get_user_with_events_query()
        query = query.limit(1)
        raw_results = self.session.execute(query).first()
        if raw_results is None:
            return None
        user: User = raw_results[0]
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
