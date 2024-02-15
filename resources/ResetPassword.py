from werkzeug.security import generate_password_hash
from flask_restful import Resource
from flask import request
from middleware.reset_token_queries import (
    check_reset_token,
    add_reset_token,
    delete_reset_token,
)
from datetime import datetime as dt


class ResetPassword(Resource):
    def __init__(self, **kwargs):
        self.psycopg2_connection = kwargs["psycopg2_connection"]

    def get(self, token):
        try:
            cursor = self.psycopg2_connection.cursor()
            token_data = check_reset_token(cursor, token)
            if "create_date" not in token_data:
                return {"message": "The submitted token is invalid"}, 400

            token_create_date = token_data["create_date"]
            token_expired = (dt.utcnow() - token_create_date).total_seconds() > 300
            delete_reset_token(cursor, token_data["email"], token)
            if token_expired:
                return {"message": "The submitted token is invalid"}, 400

            return {"message": "The submitted token is valid"}

        except Exception as e:
            self.psycopg2_connection.rollback()
            print(str(e))
            return {"message": str(e)}, 500
