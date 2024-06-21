from flask import request, Response
from middleware.reset_token_queries import (
    check_reset_token,
    reset_token_validation,
)
from datetime import datetime as dt

from resources.PsycopgResource import PsycopgResource, handle_exceptions


class ResetTokenValidation(PsycopgResource):

    @handle_exceptions
    def post(self) -> Response:
        data = request.get_json()
        with self.psycopg2_connection.cursor() as cursor:
            response = reset_token_validation(cursor, token=data.get("token"))
        self.psycopg2_connection.commit()
        return response