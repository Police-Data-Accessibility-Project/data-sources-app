from flask import make_response, Response

from db.client.core import DatabaseClient
from endpoints.instantiations.user.by_id.get.recent_searches.query import (
    GetUserRecentSearchesQueryBuilder,
)
from middleware.security.access_info.primary import AccessInfoPrimary


def get_user_recent_searches(
    db_client: DatabaseClient, access_info: AccessInfoPrimary
) -> Response:
    recent_searches: dict = db_client.run_query_builder(
        GetUserRecentSearchesQueryBuilder(access_info.get_user_id())
    )

    return make_response(recent_searches)
