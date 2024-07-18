from flask import request, Response
from flask_restx import fields

from middleware.reset_token_queries import request_reset_password
from utilities.namespace import create_namespace

from resources.PsycopgResource import PsycopgResource, handle_exceptions

namespace_request_reset_password = create_namespace()

email_model = namespace_request_reset_password.model(
    "Email",
    {
        "email": fields.String(
            required=True,
            description="The email of the user",
            example="test@example.com"
        ),
    },
)

@namespace_request_reset_password.route("/request-reset-password")
class RequestResetPassword(PsycopgResource):
    """
    Provides a resource for users to request a password reset. Generates a reset token
    and sends an email to the user with instructions on how to reset their password.
    """

    @handle_exceptions
    @namespace_request_reset_password.expect(email_model)
    @namespace_request_reset_password.response(200, "OK; Password reset request successful")
    @namespace_request_reset_password.response(500, "Internal server error")
    @namespace_request_reset_password.doc(
        description="Allows a user to request a password reset. Generates a reset token and sends an email with instructions on how to reset their password."
    )
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
