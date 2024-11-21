from flask import request, Response
from flask_restx import fields

from middleware.access_logic import (
    RESET_PASSWORD_AUTH_INFO,
    PasswordResetTokenAccessInfo,
)
from middleware.decorators import endpoint_info_2
from middleware.primary_resource_logic.reset_token_queries import (
    reset_token_validation,
)
from resources.endpoint_schema_config import SchemaConfigs
from resources.resource_helpers import ResponseInfo

from utilities.namespace import create_namespace
from resources.PsycopgResource import PsycopgResource, handle_exceptions

namespace_reset_token_validation = create_namespace()


@namespace_reset_token_validation.route("/reset-token-validation")
class ResetTokenValidation(PsycopgResource):

    @endpoint_info_2(
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
