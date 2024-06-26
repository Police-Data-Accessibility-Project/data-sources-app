from werkzeug.security import generate_password_hash
from flask import request, Response
from middleware.reset_token_queries import (
    reset_password,
)
from datetime import datetime as dt
from typing import Dict, Any

from resources.PsycopgResource import PsycopgResource, handle_exceptions


class ResetPassword(PsycopgResource):
    """
    Provides a resource for users to reset their password using a valid reset token.
    If the token is valid and not expired, allows the user to set a new password.
    """

    @handle_exceptions
    def post(self) -> Response:
        """
        Processes a password reset request. Validates the provided reset token and,
        if valid, updates the user's password with the new password provided in the request.

        Returns:
        - A dictionary containing a message indicating whether the password was successfully updated or an error occurred.
        """
        data = request.get_json()
        with self.setup_database_client() as db_client:
            response = reset_password(
                db_client, token=data.get("token"), password=data.get("password")
            )

        return response
