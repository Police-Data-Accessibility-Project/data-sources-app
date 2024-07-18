from flask import request, Response
from flask_restx import fields

from middleware.login_queries import (
    refresh_session,
)

from utilities.namespace import create_namespace
from resources.PsycopgResource import PsycopgResource, handle_exceptions

namespace_refresh_session = create_namespace()

session_token_model = namespace_refresh_session.model(
    "SessionToken",
    {
        "session_token": fields.String(
            required=True,
            description="The session token",
            example="2bd77a1d7ef24a1dad3365b8a5c6994e"
        ),
    },
)

@namespace_refresh_session.route("/refresh-session")
class RefreshSession(PsycopgResource):
    """
    Provides a resource for refreshing a user's session token.
    If the provided session token is valid and not expired, it is replaced with a new one.
    """

    @handle_exceptions
    @namespace_refresh_session.expect(session_token_model)
    @namespace_refresh_session.response(
        200, "OK; Successful session refresh"
    )
    @namespace_refresh_session.response(500, "Internal server error")
    @namespace_refresh_session.response(
        403, "Forbidden invalid old session token"
    )
    @namespace_refresh_session.doc(
        description="Allows a user to refresh their session token."
    )
    def post(self) -> Response:
        """
        Processes the session token refresh request. If the provided session token is valid,
        it generates a new session token, invalidates the old one, and returns the new token.

        Returns:
        - A dictionary containing a message of success or failure, and the new session token if successful.
        """
        data = request.get_json()
        old_token = data.get("session_token")
        with self.setup_database_client() as db_client:
            response = refresh_session(db_client, old_token)
        return response
