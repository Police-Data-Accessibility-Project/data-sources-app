from flask import request, Response
from flask_restx import fields

from middleware.access_logic import NO_AUTH_INFO, AccessInfo
from middleware.decorators import endpoint_info_2
from middleware.primary_resource_logic.reset_token_queries import request_reset_password
from resources.endpoint_schema_config import SchemaConfigs
from resources.resource_helpers import ResponseInfo
from utilities.namespace import create_namespace

from resources.PsycopgResource import PsycopgResource, handle_exceptions

namespace_request_reset_password = create_namespace()

@namespace_request_reset_password.route("/request-reset-password")
class RequestResetPassword(PsycopgResource):
    """
    Provides a resource for users to request a password reset. Generates a reset token
    and sends an email to the user with instructions on how to reset their password.
    """

    @endpoint_info_2(
        namespace=namespace_request_reset_password,
        auth_info=NO_AUTH_INFO,
        schema_config=SchemaConfigs.REQUEST_RESET_PASSWORD,
        response_info=ResponseInfo(
            response_dictionary={
                200: "OK; Password reset request successful",
                500: "Internal server error",
            }
        ),
        description = "Allows a user to request a password reset. Generates sends an email with instructions on how to reset their password."
    )
    def post(self, access_info: AccessInfo) -> Response:
        """
        Processes a password reset request. Checks if the user's email exists in the database,
        generates a reset token, and sends an email with the reset link.

        Returns:
        - A dictionary containing a success message and the reset token, or an error message if an exception occurs.
        """
        return self.run_endpoint(
            request_reset_password,
            schema_populate_parameters=SchemaConfigs.REQUEST_RESET_PASSWORD.value.get_schema_populate_parameters()
        )
