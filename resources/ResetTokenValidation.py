from flask import request, Response

from middleware.reset_token_queries import (
    reset_token_validation,
)

from utilities.namespace import create_namespace
from resources.PsycopgResource import PsycopgResource, handle_exceptions

namespace_reset_token_validation = create_namespace()

@namespace_reset_token_validation.route("/reset-token-validation")
class ResetTokenValidation(PsycopgResource):

    @handle_exceptions
    def post(self) -> Response:
        data = request.get_json()
        with self.setup_database_client() as db_client:
            response = reset_token_validation(db_client, token=data.get("token"))
        return response
