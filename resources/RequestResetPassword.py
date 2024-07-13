from flask import request, Response

from middleware.reset_token_queries import request_reset_password
from utilities.namespace import create_namespace

from resources.PsycopgResource import PsycopgResource, handle_exceptions

namespace_request_reset_password = create_namespace()

@namespace_request_reset_password.route("/request-reset-password")
class RequestResetPassword(PsycopgResource):
    """
    Provides a resource for users to request a password reset. Generates a reset token
    and sends an email to the user with instructions on how to reset their password.
    """

    @handle_exceptions
    def post(self) -> Response:
        """
        Processes a password reset request. Checks if the user's email exists in the database,
        generates a reset token, and sends an email with the reset link.

        Returns:
        - A dictionary containing a success message and the reset token, or an error message if an exception occurs.
        """
        data = request.get_json()
        email = data.get("email")
        with self.setup_database_client() as db_client:
            response = request_reset_password(db_client, email)
        return response
