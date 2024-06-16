from flask import request
from middleware.reset_token_queries import (
    check_reset_token,
)
from datetime import datetime as dt
from http import HTTPStatus

from resources.PsycopgResource import PsycopgResource


class ResetTokenValidation(PsycopgResource):

    def post(self):
        try:
            data = request.get_json()
            token = data.get("token")
            cursor = self.psycopg2_connection.cursor()
            token_data = check_reset_token(cursor, token)
            if "create_date" not in token_data:
                return {"message": "The submitted token is invalid"}, HTTPStatus.BAD_REQUEST

            token_create_date = token_data["create_date"]
            token_expired = (dt.utcnow() - token_create_date).total_seconds() > 900

            if token_expired:
                return {"message": "The submitted token is invalid"}, HTTPStatus.BAD_REQUEST

            return {"message": "Token is valid"}

        except Exception as e:
            self.psycopg2_connection.rollback()
            print(str(e))
            return {"message": str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR
