from sqlalchemy.orm import Mapped

from db.models.mixins import CreatedAtMixin
from db.models.templates.standard import StandardBase
from middleware.enums import Relations


class NotificationLog(StandardBase, CreatedAtMixin):
    __tablename__ = Relations.NOTIFICATION_LOG.value

    user_count: Mapped[int]
