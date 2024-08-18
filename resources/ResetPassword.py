from flask import request, Response
from flask_restx import fields

from middleware.reset_token_queries import (
    reset_password,
    RequestResetPasswordRequest,
)
from resources.resource_helpers import create_user_model
from utilities.namespace import create_namespace

from resources.PsycopgResource import PsycopgResource, handle_exceptions
from utilities.populate_dto_with_request_content import (
    populate_dto_with_request_content,
    SourceMappingEnum,
)

namespace_reset_password = create_namespace()

reset_password_model = namespace_reset_password.model(
    "ResetPassword",
    {
        "token": fields.String(
            required=True,
            description="The Reset password token to validate",
            example="2bd77a1d7ef24a1dad3365b8a5c6994e",
        ),
        "password": fields.String(
            required=True, description="The new password to set", example="newpassword"
        ),
    },
)


@namespace_reset_password.route("/reset-password")
class ResetPassword(PsycopgResource):
    """
    Provides a resource for users to reset their password using a valid reset token.
    If the token is valid and not expired, allows the user to set a new password.
    """

    @handle_exceptions
    @namespace_reset_password.expect(reset_password_model)
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
        dto = populate_dto_with_request_content(
            object_class=RequestResetPasswordRequest,
            source=SourceMappingEnum.JSON,
        )
        with self.setup_database_client() as db_client:
            response = reset_password(
                db_client, dto=dto
            )

        return response
