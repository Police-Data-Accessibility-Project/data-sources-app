from flask import Response

from middleware.access_logic import RESET_PASSWORD_AUTH_INFO, PasswordResetTokenAccessInfo
from middleware.decorators import endpoint_info_2
from middleware.primary_resource_logic.reset_token_queries import (
    reset_password,
    ResetPasswordSchema,
    ResetPasswordDTO,
)
from resources.endpoint_schema_config import SchemaConfigs
from resources.resource_helpers import ResponseInfo
from utilities.namespace import create_namespace

from resources.PsycopgResource import PsycopgResource, handle_exceptions
from middleware.schema_and_dto_logic.dynamic_logic.dynamic_schema_documentation_construction import (
    get_restx_param_documentation,
)
from middleware.schema_and_dto_logic.non_dto_dataclasses import SchemaPopulateParameters

namespace_reset_password = create_namespace()

@namespace_reset_password.route("/reset-password")
class ResetPassword(PsycopgResource):
    """
    Provides a resource for users to reset their password using a valid reset token.
    If the token is valid and not expired, allows the user to set a new password.
    """

    @endpoint_info_2(
        namespace=namespace_reset_password,
        auth_info=RESET_PASSWORD_AUTH_INFO,
        schema_config=SchemaConfigs.RESET_PASSWORD,
        response_info=ResponseInfo(
            success_message="Password reset successful",
        ),
        description="Allows a user to reset their password using a valid reset token.",
    )
    def post(self, access_info: PasswordResetTokenAccessInfo) -> Response:
        """
        Processes a password reset request. Validates the provided reset token and,
        if valid, updates the user's password with the new password provided in the request.

        Returns:
        - A dictionary containing a message indicating whether the password was successfully updated or an error occurred.
        """
        return self.run_endpoint(
            wrapper_function=reset_password,
            schema_populate_parameters=SchemaConfigs.RESET_PASSWORD.value.get_schema_populate_parameters(),
            access_info=access_info,
        )
