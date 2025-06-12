from flask import Response

from endpoints.schema_config.instantiations.reset_password.request import (
    RequestResetPasswordEndpointSchemaConfig,
)
from middleware.access_logic import AccessInfoPrimary
from middleware.security.authentication_info import NO_AUTH_INFO
from middleware.decorators.decorators import endpoint_info
from middleware.primary_resource_logic.reset_token_queries import request_reset_password
from endpoints.schema_config.enums import SchemaConfigs
from endpoints._helpers.response_info import ResponseInfo
from utilities.namespace import create_namespace, AppNamespaces

from endpoints.psycopg_resource import PsycopgResource

namespace_request_reset_password = create_namespace(AppNamespaces.AUTH)


@namespace_request_reset_password.route("/request-reset-password")
class RequestResetPassword(PsycopgResource):
    """
    Provides a resource for users to request a password reset. Generates a reset token
    and sends an email to the user with instructions on how to reset their password.
    """

    @endpoint_info(
        namespace=namespace_request_reset_password,
        auth_info=NO_AUTH_INFO,
        schema_config=SchemaConfigs.REQUEST_RESET_PASSWORD,
        response_info=ResponseInfo(
            response_dictionary={
                200: "OK; Password reset request successful",
                500: "Internal server error",
            }
        ),
        description="Allows a user to request a password reset. Generates sends an email with instructions on how to reset their password.",
    )
    def post(self, access_info: AccessInfoPrimary) -> Response:
        """
        Processes a password reset request. Checks if the user's email exists in the database,
        generates a reset token, and sends an email with the reset link.

        Returns:
        - A dictionary containing a success message and the reset token, or an error message if an exception occurs.
        """
        return self.run_endpoint(
            request_reset_password,
            schema_populate_parameters=RequestResetPasswordEndpointSchemaConfig.get_schema_populate_parameters(),
        )
