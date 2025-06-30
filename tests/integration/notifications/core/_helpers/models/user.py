from pydantic import BaseModel

from tests.integration.notifications.core._helpers.expected_event_info import (
    ExpectedEventInfo,
)


class NotificationsTestUserInfo(BaseModel):
    user_id: int
    user_email: str
    expected_events: list[ExpectedEventInfo]
