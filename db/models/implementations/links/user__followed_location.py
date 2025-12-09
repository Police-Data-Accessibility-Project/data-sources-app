from sqlalchemy.orm import relationship

from db.models.mixins import CountMetadata, CreatedAtMixin, UserIDMixin, LocationIDMixin
from db.models.templates.standard import StandardBase
from middleware.enums import Relations


class LinkUserFollowedLocation(
    StandardBase, CountMetadata, CreatedAtMixin, UserIDMixin, LocationIDMixin
):
    __tablename__ = Relations.LINK_USER_FOLLOWED_LOCATION.value

    record_types = relationship(
        "RecordType",
        secondary="public.link_follow_record_types",
        primaryjoin="LinkUserFollowedLocation.id == LinkFollowRecordType.follow_id",
        secondaryjoin="LinkFollowRecordType.record_type_id == RecordType.id",
    )
