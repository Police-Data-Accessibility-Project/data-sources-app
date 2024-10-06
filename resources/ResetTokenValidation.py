from flask import request, Response
from flask_restx import fields

from middleware.primary_resource_logic.reset_token_queries import (
    reset_token_validation,
)

from utilities.namespace import create_namespace
from resources.PsycopgResource import PsycopgResource, handle_exceptions

namespace_reset_token_validation = create_namespace()
reset_token_model = namespace_reset_token_validation.model(
    "ResetToken",
    {
        "token": fields.String(
            required=True,
            description="The Reset password token to validate",
            example="2bd77a1d7ef24a1dad3365b8a5c6994e",
        ),
    },
)


@namespace_reset_token_validation.route("/reset-token-validation")
class ResetTokenValidation(PsycopgResource):

    @handle_exceptions
    @namespace_reset_token_validation.expect(reset_token_model)
    @namespace_reset_token_validation.response(
        200, "OK; Reset password token validated"
    )
    @namespace_reset_token_validation.response(500, "Internal server error")
    @namespace_reset_token_validation.response(
        400, "Bad request; Request token is invalid"
    )
    @namespace_reset_token_validation.doc(description="Validates a reset token.")
    def post(self) -> Response:
        """
        If the token matches a row in the database, 'Token is valid' is returned.
        :return:
        """
        return self.run_endpoint(
            reset_token_validation, token=request.json.get("token")
        )
