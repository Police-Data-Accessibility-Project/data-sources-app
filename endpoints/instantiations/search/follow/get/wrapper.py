from typing import Any

from flask import Response, make_response

from db.client.core import DatabaseClient
from endpoints.instantiations.search.follow.get.query.core import GetUserFollowedSearchesQueryBuilder
from middleware.security.access_info.primary import AccessInfoPrimary


def get_followed_searches(
    db_client: DatabaseClient,
    access_info: AccessInfoPrimary,
) -> Response:
    results: dict[str, Any] = db_client.run_query_builder(
        GetUserFollowedSearchesQueryBuilder(user_id=access_info.get_user_id())
    )
    results["message"] = "Followed searches found."
    return make_response(results)
