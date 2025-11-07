from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError

from db.models.exceptions import LocationNotFound
from db.models.implementations.links.follow__record_types import LinkFollowRecordType
from db.models.implementations.links.user__followed_location import LinkUserFollowedLocation
from db.queries.instantiations.search.follow.base import FollowBaseQueryBuilder


class CreateFollowQueryBuilder(FollowBaseQueryBuilder):
    def add_or_get_follow(self):
        query = (
            select(LinkUserFollowedLocation.id)
            .where(LinkUserFollowedLocation.location_id == self.location_id)
            .where(LinkUserFollowedLocation.user_id == self.user_id)
        )
        follow_id = self.session.execute(query).scalar()

        if follow_id is None:
            follow = LinkUserFollowedLocation(
                location_id=self.location_id, user_id=self.user_id
            )
            self.session.add(follow)
            self.session.flush()
            follow_id = follow.id

        return follow_id

    def run(self) -> None:
        # Follow location or get existing followed search
        try:
            follow_id = self.add_or_get_follow()
        except IntegrityError as e:
            if 'not present in table "locations"' in str(e):
                raise LocationNotFound
            raise e

        # Add all record types to the user's follows, if they don't already exist
        rt_ids = self.record_type_ids
        if len(rt_ids) == 0:
            return
        d_rows = []
        for rt_id in rt_ids:
            d_row = {"follow_id": follow_id, "record_type_id": rt_id}
            d_rows.append(d_row)
        stmt = insert(LinkFollowRecordType).values(d_rows)
        stmt = stmt.on_conflict_do_nothing(
            index_elements=["follow_id", "record_type_id"]
        )
        self.session.execute(stmt)
