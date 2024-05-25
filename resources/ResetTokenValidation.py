from flask import request
from flask_restx import abort

from middleware.reset_token_queries import (
    check_reset_token,
)
from datetime import datetime as dt

from resources.PsycopgResource import PsycopgResource, handle_exceptions


class ResetTokenValidation(PsycopgResource):

    @handle_exceptions
    def post(self):
        data = request.get_json()
        token = data.get("token")
        cursor = self.psycopg2_connection.cursor()
        token_data = check_reset_token(cursor, token)
        if "create_date" not in token_data:
            return {"message": "The submitted token is invalid"}, 400

        token_create_date = token_data["create_date"]
        token_expired = (dt.utcnow() - token_create_date).total_seconds() > 900

        if token_expired:
            abort(code=400, message="The submitted token is invalid")

        return {"message": "Token is valid"}
