from typing import Any

from db.queries.search.follow.national.base import FollowNationalBaseQueryBuilder


class FollowNationalQueryBuilder(FollowNationalBaseQueryBuilder):

    def run(self) -> Any:
        # Add all record types to the user's follows, if they don't already exist
        rt_ids = self.record_type_ids
