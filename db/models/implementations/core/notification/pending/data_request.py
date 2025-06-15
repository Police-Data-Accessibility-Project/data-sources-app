from typing import get_args

from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column

from db.models.mixins import CreatedAtMixin, DataRequestIDMixin
from db.models.templates.standard import StandardBase
from db.models.types import EventTypeDataRequestLiteral
from middleware.enums import Relations


class DataRequestPendingEventNotification(
    StandardBase, CreatedAtMixin, DataRequestIDMixin
):
    __tablename__ = Relations.DATA_REQUESTS_PENDING_EVENT_NOTIFICATIONS.value
    event_type: Mapped[EventTypeDataRequestLiteral] = mapped_column(
        Enum(*get_args(EventTypeDataRequestLiteral), name="event_type_data_request")
    )
