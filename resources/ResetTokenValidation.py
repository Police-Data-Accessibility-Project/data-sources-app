from flask_restful import Resource
from flask import request
from middleware.reset_token_queries import (
    check_reset_token,
)
from datetime import datetime as dt


class ResetTokenValidation(Resource):
    def __init__(self, **kwargs):
        self.psycopg2_connection = kwargs["psycopg2_connection"]

    def post(self):
        try:
            data = request.get_json()
            token = data.get("token")
            cursor = self.psycopg2_connection.cursor()
            token_data = check_reset_token(cursor, token)
            if "create_date" not in token_data:
                return {"message": "The submitted token is invalid"}, 400

            token_create_date = token_data["create_date"]
            token_expired = (dt.utcnow() - token_create_date).total_seconds() > 900

            if token_expired:
                return {"message": "The submitted token is invalid"}, 400

            return {"message": "Token is valid"}

        except Exception as e:
            self.psycopg2_connection.rollback()
            print(str(e))
            return {"message": str(e)}, 500
