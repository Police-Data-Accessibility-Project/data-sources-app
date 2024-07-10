from flask import request, Response
from middleware.reset_token_queries import (
    reset_token_validation,
)
from datetime import datetime as dt

from resources.PsycopgResource import PsycopgResource, handle_exceptions


class ResetTokenValidation(PsycopgResource):

    @handle_exceptions
    def post(self) -> Response:
        data = request.get_json()
        with self.setup_database_client() as db_client:
            response = reset_token_validation(db_client, token=data.get("token"))
        return response
