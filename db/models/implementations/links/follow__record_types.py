from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db.models.mixins import RecordTypeIDMixin
from db.models.templates.standard import StandardBase
from middleware.enums import Relations


class LinkFollowRecordType(StandardBase, RecordTypeIDMixin):
    __tablename__ = Relations.LINK_FOLLOW_RECORD_TYPES.value

    follow_id: Mapped[int] = mapped_column(
        ForeignKey("public.link_user_followed_location.id")
    )
