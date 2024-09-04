from flask import Response

from middleware.primary_resource_logic.reset_token_queries import (
    reset_password,
    RequestResetPasswordRequest,
    RequestResetPasswordRequestSchema,
)
from utilities.namespace import create_namespace

from resources.PsycopgResource import PsycopgResource, handle_exceptions
from middleware.schema_and_dto_logic.dynamic_schema_documentation_construction import (
    get_restx_param_documentation, )
from middleware.schema_and_dto_logic.non_dto_dataclasses import SchemaPopulateParameters

namespace_reset_password = create_namespace()

doc_info = get_restx_param_documentation(
    namespace=namespace_reset_password,
    schema_class=RequestResetPasswordRequestSchema,
    model_name="ResetPassword",
)

reset_password_model = doc_info.model

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
        return self.run_endpoint(
            wrapper_function=reset_password,
            schema_populate_parameters=SchemaPopulateParameters(
                schema_class=RequestResetPasswordRequestSchema,
                dto_class=RequestResetPasswordRequest,
            )
        )
