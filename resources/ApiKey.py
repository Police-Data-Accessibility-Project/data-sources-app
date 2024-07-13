from flask import request, Response

from middleware.login_queries import get_api_key_for_user
from utilities.namespace import create_namespace

from resources.PsycopgResource import PsycopgResource, handle_exceptions

namespace_api_key = create_namespace()

@namespace_api_key.route("/api_key")
class ApiKey(PsycopgResource):
    """Represents a resource for generating an API key for authenticated users."""

    @handle_exceptions
    def get(self) -> Response:
        """
        Authenticates a user based on provided credentials and generates an API key.

        Reads the 'email' and 'password' from the JSON body of the request, validates the user,
        and if successful, generates and returns a new API key.

        Returns:
        - dict: A dictionary containing the generated API key, or None if an error occurs.
        """
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        with self.setup_database_client() as db_client:
            response = get_api_key_for_user(db_client, email, password)
        return response
