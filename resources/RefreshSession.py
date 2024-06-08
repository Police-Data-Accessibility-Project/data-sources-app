from flask import request, Response

from middleware.custom_exceptions import TokenNotFoundError
from middleware.login_queries import (
    get_session_token_user_data,
    create_session_token,
    delete_session_token,
    refresh_session,
)
from typing import Dict, Any

from resources.PsycopgResource import PsycopgResource, handle_exceptions


class RefreshSession(PsycopgResource):
    """
    Provides a resource for refreshing a user's session token.
    If the provided session token is valid and not expired, it is replaced with a new one.
    """

    @handle_exceptions
    def post(self) -> Response:
        """
        Processes the session token refresh request. If the provided session token is valid,
        it generates a new session token, invalidates the old one, and returns the new token.

        Returns:
        - A dictionary containing a message of success or failure, and the new session token if successful.
        """
        data = request.get_json()
        old_token = data.get("session_token")
        with self.psycopg2_connection.cursor() as cursor:
            response = refresh_session(cursor, old_token)
            self.psycopg2_connection.commit()
        return response
