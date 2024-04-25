from werkzeug.security import check_password_hash
from flask import request
from middleware.login_queries import login_results, create_session_token
from resources.PsycopgResource import PsycopgResource


class Login(PsycopgResource):
    """
    A resource for authenticating users. Allows users to log in using their email and password.
    """

    def post(self):
        """
        Processes the login request. Validates user credentials against the stored hashed password and,
        if successful, generates a session token for the user.

        Returns:
        - A dictionary containing a message of success or failure, and the session token if successful.
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
