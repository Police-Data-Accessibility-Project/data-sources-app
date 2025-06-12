from flask import Response

from endpoints.schema_config.instantiations.reset_password.reset import (
    ResetPasswordEndpointSchemaConfig,
)
from middleware.access_logic import (
    PasswordResetTokenAccessInfo,
)
from middleware.security.authentication_info import RESET_PASSWORD_AUTH_INFO
from middleware.decorators.decorators import endpoint_info
from middleware.primary_resource_logic.reset_token_queries import (
    reset_password,
)
from endpoints.schema_config.enums import SchemaConfigs
from endpoints._helpers.response_info import ResponseInfo
from utilities.namespace import create_namespace, AppNamespaces

from endpoints.psycopg_resource import PsycopgResource

namespace_reset_password = create_namespace(AppNamespaces.AUTH)


@namespace_reset_password.route("/reset-password")
class ResetPassword(PsycopgResource):
    """
    Provides a resource for users to reset their password using a valid reset token.
    If the token is valid and not expired, allows the user to set a new password.
    """

    @endpoint_info(
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
            schema_populate_parameters=ResetPasswordEndpointSchemaConfig.get_schema_populate_parameters(),
            access_info=access_info,
        )
