from flask_restful import Resource
from flask import request
from middleware.login_queries import token_results, create_session_token
from datetime import datetime as dt


class RefreshSession(Resource):
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
            old_token = data.get("session_token")
            cursor = self.psycopg2_connection.cursor()
            user_data = token_results(cursor, old_token)
            cursor.execute(
                f"delete from session_tokens where token = '{old_token}' and expiration_date < '{dt.utcnow()}'"
            )
            self.psycopg2_connection.commit()

            if "id" in user_data:
                token = create_session_token(
                    cursor, user_data["id"], user_data["email"]
                )
                self.psycopg2_connection.commit()
                return {
                    "message": "Successfully refreshed session token",
                    "data": token,
                }

        except Exception as e:
            self.psycopg2_connection.rollback()
            print(str(e))
            return {"message": str(e)}, 500
