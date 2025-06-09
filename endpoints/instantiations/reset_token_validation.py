from flask import Response

from middleware.access_logic import (
    PasswordResetTokenAccessInfo,
)
from middleware.authentication_info import RESET_PASSWORD_AUTH_INFO
from middleware.decorators import endpoint_info
from middleware.primary_resource_logic.reset_token_queries import (
    reset_token_validation,
)
from endpoints.schema_config.enums import SchemaConfigs
from endpoints._helpers.response_info import ResponseInfo

from utilities.namespace import create_namespace, AppNamespaces
from endpoints.psycopg_resource import PsycopgResource

namespace_reset_token_validation = create_namespace(AppNamespaces.AUTH)


@namespace_reset_token_validation.route("/reset-token-validation")
class ResetTokenValidation(PsycopgResource):

    @endpoint_info(
        namespace=namespace_reset_token_validation,
        auth_info=RESET_PASSWORD_AUTH_INFO,
        schema_config=SchemaConfigs.RESET_TOKEN_VALIDATION,
        response_info=ResponseInfo(
            response_dictionary={
                200: "OK; Reset password token validated",
                500: "Internal server error",
                400: "Bad request; token is invalid",
            }
        ),
    )
    def post(self, access_info: PasswordResetTokenAccessInfo) -> Response:
        """
        If the token matches a row in the database, 'Token is valid' is returned.
        :return:
        """
        return self.run_endpoint(reset_token_validation, token=access_info.reset_token)
