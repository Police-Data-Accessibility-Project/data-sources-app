from werkzeug.security import check_password_hash
from flask_restful import Resource
from flask import request
from middleware.login_queries import login_results
import jwt
import os
import datetime


class Login(Resource):
    def __init__(self, **kwargs):
        self.psycopg2_connection = kwargs["psycopg2_connection"]

    def post(self):
        """
        Login function: allows a user to login using their email and password as credentials
        The password is compared to the hashed password stored in the users table
        Once the password is verified, an API key is generated, which is stored in the users table and sent to the verified user
        """
        try:
            data = request.get_json()
            email = data.get("email")
            password = data.get("password")
            cursor = self.psycopg2_connection.cursor()

            user_data = login_results(cursor, email)

            if "password_digest" in user_data and check_password_hash(
                user_data["password_digest"], password
            ):
                payload = {
                    "exp": datetime.datetime.utcnow()
                    + datetime.timedelta(days=0, seconds=300),
                    "iat": datetime.datetime.utcnow(),
                    "sub": 1,
                }
                session_token = jwt.encode(
                    payload, os.getenv("SECRET_KEY"), algorithm="HS256"
                )
                return {
                    "message": "Successfully logged in",
                    "data": session_token,
                }

        except Exception as e:
            self.psycopg2_connection.rollback()
            print(str(e))
            return {"message": str(e)}, 500
