from flask import Response, make_response

from db.client.core import DatabaseClient
from middleware.security.access_info.primary import AccessInfoPrimary


def get_followed_searches(
    db_client: DatabaseClient,
    access_info: AccessInfoPrimary,
) -> Response:
    results = db_client.get_user_followed_searches(
        user_id=access_info.get_user_id(),
    )
    results["message"] = "Followed searches found."
    return make_response(results)
