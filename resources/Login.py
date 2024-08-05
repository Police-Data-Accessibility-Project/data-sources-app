from flask import request, Response
from flask_restx import fields

from config import limiter
from middleware.login_queries import try_logging_in
from resources.resource_helpers import create_user_model
from utilities.namespace import create_namespace

from resources.PsycopgResource import PsycopgResource, handle_exceptions

namespace_login = create_namespace()
user_model = create_user_model(namespace_login)

@namespace_login.route("/login")
class Login(PsycopgResource):
    """
    A resource for authenticating users. Allows users to log in using their email and password.
    """

    @handle_exceptions
    @namespace_login.expect(user_model)
    @namespace_login.response(200, "Success: User logged in")
    @namespace_login.response(500, "Error: Internal server error")
    @namespace_login.response(400, "Error: Bad Request Missing or bad API key")
    @namespace_login.response(403, "Error: Forbidden")
    @namespace_login.doc(
        description="Allows a user to log in. If successful, returns a session token.",
    )
    @limiter.limit("5 per minute")
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
        return response
