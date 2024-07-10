from flask_restx import abort
from werkzeug.security import check_password_hash
from flask import request, Response
from middleware.login_queries import try_logging_in

from resources.PsycopgResource import PsycopgResource, handle_exceptions


class Login(PsycopgResource):
    """
    A resource for authenticating users. Allows users to log in using their email and password.
    """

    @handle_exceptions
    def post(self) -> Response:
        """
        Processes the login request. Validates user credentials against the stored hashed password and,
        if successful, generates a session token for the user.

        Returns:
        - A dictionary containing a message of success or failure, and the session token if successful.
        """
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        with self.setup_database_client() as db_client:
            response = try_logging_in(db_client, email, password)
            self.psycopg2_connection.commit()
        return response
