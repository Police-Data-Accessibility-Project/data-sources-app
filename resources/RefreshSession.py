from flask import request
from middleware.login_queries import token_results, create_session_token, delete_session_token
from typing import Dict, Any

from resources.PsycopgResource import PsycopgResource, handle_exceptions


class RefreshSession(PsycopgResource):
    """
    Provides a resource for refreshing a user's session token.
    If the provided session token is valid and not expired, it is replaced with a new one.
    """

    @handle_exceptions
    def post(self) -> Dict[str, Any]:
        """
        Processes the session token refresh request. If the provided session token is valid,
        it generates a new session token, invalidates the old one, and returns the new token.

        Returns:
        - A dictionary containing a message of success or failure, and the new session token if successful.
        """
        data = request.get_json()
        old_token = data.get("session_token")
        cursor = self.psycopg2_connection.cursor()
        user_data = token_results(cursor, old_token)
        delete_session_token(cursor, old_token)
        self.psycopg2_connection.commit()

        if "id" in user_data:
            token = create_session_token(cursor, user_data["id"], user_data["email"])
            return {
                "message": "Successfully refreshed session token",
                "data": token,
            }
        self.psycopg2_connection.commit()

        return {"message": "Invalid session token"}, 403
