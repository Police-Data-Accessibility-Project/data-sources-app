from flask import request, Response
from flask_restx import fields

from middleware.reset_token_queries import (
    reset_token_validation,
)

from utilities.namespace import create_namespace
from resources.PsycopgResource import PsycopgResource, handle_exceptions

namespace_reset_token_validation = create_namespace()

@namespace_reset_token_validation.route("/reset-token-validation")
class ResetTokenValidation(PsycopgResource):

    @handle_exceptions
    @namespace_reset_token_validation.param(
        name="token",
        description="The Reset password token to validate",
        _in="query",
        type="string",
    )
    @namespace_reset_token_validation.response(200, "OK; Reset password token validated")
    @namespace_reset_token_validation.response(500, "Internal server error")
    @namespace_reset_token_validation.response(400, "Bad request; Request token is invalid")
    @namespace_reset_token_validation.doc(
        description="Validates a reset token."
    )
    def post(self) -> Response:
        """
        If the token matches a row in the database, 'Token is valid' is returned.
        :return:
        """
        data = request.get_json()
        with self.setup_database_client() as db_client:
            response = reset_token_validation(db_client, token=data.get("token"))
        return response
