from unittest.mock import MagicMock

from pydantic import BaseModel


class SendViaMailgunMocks(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    data_sources: MagicMock
    data_requests: MagicMock
    contact: MagicMock
    notifications: MagicMock
    signup: MagicMock
    webhook_logic: MagicMock
