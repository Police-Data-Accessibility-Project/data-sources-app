from unittest.mock import call

from db.dtos.event_batch import EventBatch
from tests.integration.notifications.core._helpers.call_checker.event_info_checker import (
    EventInfoChecker,
)
from tests.integration.notifications.core._helpers.expected_event_info import (
    ExpectedEventInfo,
)
from tests.integration.notifications.core._helpers.models.user import (
    NotificationsTestUserInfo,
)

CallType = type(call)


class EventBatchChecker:
    """Used to check calls to `format_and_send_notifications`"""

    def __init__(
        self,
        batches: list[EventBatch],
    ):
        self._batch_dict: dict[int, EventBatch] = self._build_call_dict(batches)

    @staticmethod
    def _build_call_dict(batches: list[EventBatch]):
        d = {}
        for batch in batches:
            assert isinstance(batch, EventBatch)
            user_id = batch.user_id
            d[user_id] = batch
        return d

    def check_user(self, info: NotificationsTestUserInfo):
        user_id = info.user_id
        self._check_email(user_id, info.user_email)
        self._check_event_infos(user_id, info.expected_events)

    def _check_email(self, user_id: int, expected_email: str):
        event_batch = self._batch_dict[user_id]
        assert event_batch.user_email == expected_email

    def _check_event_infos(
        self, user_id: int, expected_event_infos: list[ExpectedEventInfo]
    ):
        event_batch = self._batch_dict[user_id]
        events = event_batch.events
        checker = EventInfoChecker(event_infos=events)
        assert len(events) == len(expected_event_infos)
        for expected_event_info in expected_event_infos:
            checker.check_event_info(expected_event_info)
