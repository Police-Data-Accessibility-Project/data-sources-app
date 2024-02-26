from werkzeug.security import check_password_hash
from flask_restful import Resource
from flask import request
from middleware.login_queries import login_results, create_session_token


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
                token = create_session_token(cursor, user_data["id"], email)
                self.psycopg2_connection.commit()
                return {
                    "message": "Successfully logged in",
                    "data": token,
                }

            return {"message": "Invalid email or password"}, 401

        except Exception as e:
            self.psycopg2_connection.rollback()
            print(str(e))
            return {"message": str(e)}, 500
