from flask import Response

from db.client import DatabaseClient
from middleware.access_logic import AccessInfoPrimary
from middleware.flask_response_manager import FlaskResponseManager


def get_followed_searches(
    db_client: DatabaseClient,
    access_info: AccessInfoPrimary,
) -> Response:
    results = db_client.get_user_followed_searches(
        left_id=access_info.get_user_id(),
    )
    results["message"] = "Followed searches found."
    return FlaskResponseManager.make_response(results)
