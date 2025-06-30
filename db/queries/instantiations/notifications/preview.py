from typing import override, final

from db.dtos.event_batch import EventBatch
from db.dtos.event_info import EventInfo
from db.enums import EntityType
from db.models.implementations.core.user.core import User
from db.queries.builder.core import QueryBuilderBase
from db.queries.instantiations.notifications.queries.user_with_events import (
    get_user_with_events_query,
)
from middleware.schema_and_dto.dtos.notifications.preview import (
    NotificationsPreviewOutput,
    NotificationsPreviewCount,
)


@final
class NotificationsPreviewQueryBuilder(QueryBuilderBase):
    def __init__(self):
        super().__init__()
        self.total_events = 0
        self.total_users = 0
        self.distinct_data_request_events: set[int] = set()
        self.distinct_data_source_events: set[int] = set()
        self.event_batches: list[EventBatch] = []

    @override
    def run(self) -> NotificationsPreviewOutput:
        query = get_user_with_events_query()
        raw_results = self.session.execute(query).all()
        for raw_result in raw_results:
            user: User = raw_result[0]
            self._process_user(user)

        return NotificationsPreviewOutput(
            counts=NotificationsPreviewCount(
                total_events=self.total_events,
                total_users=self.total_users,
                distinct_events=len(self.distinct_data_request_events)
                + len(self.distinct_data_source_events),
                distinct_data_request_events=len(self.distinct_data_request_events),
                distinct_data_source_events=len(self.distinct_data_source_events),
            ),
            batches=self.event_batches,
        )

    def _process_user(self, user: User) -> None:
        self.total_users += 1
        preview_events: list[EventInfo] = []
        for event in user.data_request_events:
            self.total_events += 1
            self.distinct_data_request_events.add(event.id)
            preview_events.append(
                EventInfo(
                    event_id=event.id,
                    entity_id=event.data_request.id,
                    entity_type=EntityType.DATA_REQUEST,
                    event_type=event.event_type,
                    entity_name=event.data_request.title,
                )
            )

        for event in user.data_source_events:
            self.total_events += 1
            self.distinct_data_source_events.add(event.id)
            preview_events.append(
                EventInfo(
                    event_id=event.id,
                    entity_id=event.data_source.id,
                    entity_type=EntityType.DATA_SOURCE,
                    event_type=event.event_type,
                    entity_name=event.data_source.name,
                )
            )

        preview_user = EventBatch(
            user_id=user.id, user_email=user.email, events=preview_events
        )
        self.event_batches.append(preview_user)
