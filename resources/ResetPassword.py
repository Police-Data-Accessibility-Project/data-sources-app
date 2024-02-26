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

    def post(self):
        try:
            data = request.get_json()
            token = data.get("token")
            password = data.get("password")
            cursor = self.psycopg2_connection.cursor()
            token_data = check_reset_token(cursor, token)
            email = token_data.get("email")
            if "create_date" not in token_data:
                return {"message": "The submitted token is invalid"}, 400

            token_create_date = token_data["create_date"]
            token_expired = (dt.utcnow() - token_create_date).total_seconds() > 300
            delete_reset_token(cursor, token_data["email"], token)
            if token_expired:
                return {"message": "The submitted token is invalid"}, 400

            password_digest = generate_password_hash(password)
            cursor = self.psycopg2_connection.cursor()
            cursor.execute(
                f"update users set password_digest = '{password_digest}' where email = '{email}'"
            )
            self.psycopg2_connection.commit()

            return {"message": "Successfully updated password"}

        except Exception as e:
            self.psycopg2_connection.rollback()
            print(str(e))
            return {"message": str(e)}, 500
