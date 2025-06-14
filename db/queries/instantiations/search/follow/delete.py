from sqlalchemy import delete

from db.models.implementations.link import (
    LinkFollowRecordType,
    LinkUserFollowedLocation,
)
from db.queries.instantiations.search.follow.base import FollowBaseQueryBuilder


class DeleteFollowQueryBuilder(FollowBaseQueryBuilder):

    def remove_follow_if_exists(self):
        query = delete(LinkUserFollowedLocation).where(
            LinkUserFollowedLocation.location_id == self.location_id,
            LinkUserFollowedLocation.user_id == self.user_id,
        )
        self.session.execute(query)

    def unfollow(self):
        rt_ids = self.record_type_ids
        # If record types are not specified, remove the follow completely
        if self.all_record_types is True:
            self.remove_follow_if_exists()
            return

        # Otherwise, remove select record types
        query = delete(LinkFollowRecordType).where(
            LinkFollowRecordType.record_type_id.in_(rt_ids)
        )
        self.session.execute(query)

    def run(self) -> None:
        self.unfollow()
