from typing import get_args

from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column

from db.models.mixins import CreatedAtMixin, DataSourceIDMixin
from db.models.templates.standard import StandardBase
from db.models.types import EventTypeDataSourceLiteral
from middleware.enums import Relations


class DataSourcePendingEventNotification(
    StandardBase, CreatedAtMixin, DataSourceIDMixin
):
    __tablename__ = Relations.DATA_SOURCES_PENDING_EVENT_NOTIFICATIONS.value

    event_type: Mapped[EventTypeDataSourceLiteral] = mapped_column(
        Enum(*get_args(EventTypeDataSourceLiteral), name="event_type_data_source")
    )
