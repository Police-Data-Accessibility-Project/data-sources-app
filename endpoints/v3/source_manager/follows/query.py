from typing import Sequence

from sqlalchemy import select, RowMapping

from db.models.implementations.links.user__followed_location import LinkUserFollowedLocation
from db.queries.builder.core import QueryBuilderBase
from endpoints.v3.source_manager.follows.response import (
    LinkUserFollow,
    GetFollowsResponse,
)

from db.helpers_ import session as sh


class GetUserFollowsSourceCollectorQueryBuilder(QueryBuilderBase):
    def run(self) -> GetFollowsResponse:
        query = select(
            LinkUserFollowedLocation.user_id,
            LinkUserFollowedLocation.location_id,
        )

        mappings: Sequence[RowMapping] = sh.mappings(session=self.session, query=query)

        links: list[LinkUserFollow] = [
            LinkUserFollow(
                user_id=mapping["user_id"],
                location_id=mapping["location_id"],
            )
            for mapping in mappings
        ]

        return GetFollowsResponse(
            follows=links,
        )
