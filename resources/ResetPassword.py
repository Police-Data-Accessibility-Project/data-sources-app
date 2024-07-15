from flask import request, Response

from middleware.reset_token_queries import (
    reset_password,
)
from utilities.namespace import create_namespace

from resources.PsycopgResource import PsycopgResource, handle_exceptions

namespace_reset_password = create_namespace()

@namespace_reset_password.route("/reset-password")
class ResetPassword(PsycopgResource):
    """
    Provides a resource for users to reset their password using a valid reset token.
    If the token is valid and not expired, allows the user to set a new password.
    """

    @handle_exceptions
    @namespace_reset_password.param(
        name="token",
        description="The Reset password token to validate",
        _in="query",
        type="string",
    )
    @namespace_reset_password.param(
        name="password",
        description="The new password to set",
        _in="query",
        type="string",
    )
    @namespace_reset_password.response(200, "OK; Password reset successful")
    @namespace_reset_password.response(500, "Internal server error")
    @namespace_reset_password.doc(
        description="Allows a user to reset their password using a valid reset token."
    )
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
