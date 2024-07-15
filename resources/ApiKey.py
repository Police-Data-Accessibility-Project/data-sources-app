from flask import request, Response
from flask_restx import fields

from middleware.login_queries import get_api_key_for_user
from utilities.namespace import create_namespace

from resources.PsycopgResource import PsycopgResource, handle_exceptions

namespace_api_key = create_namespace()

api_key_model = namespace_api_key.model(
    "ApiKey",
    {
        "api_key": fields.String(
            required=True,
            description="The generated API key",
            example="2bd77a1d7ef24a1dad3365b8a5c6994e"
        ),
    },
)

@namespace_api_key.route("/api_key")
@namespace_api_key.doc(
    description="Generates an API key for authenticated users.",
    params={
        "email": {
            "in": "query",
            "type": "string",
            "description": "The email of the user.",
        },
        "password": {
            "in": "query",
            "type": "string",
            "description": "The password of the user. Checked against the password_digest for the user with the matching \"email\" property using werkzeug.security’s check_password_hash function",
        },
    },
    responses={
        200: "Success",
        401: "Invalid email or password",
        500: "Internal server error.",
    },
)
class ApiKey(PsycopgResource):
    """Represents a resource for generating an API key for authenticated users."""

    @handle_exceptions
    @namespace_api_key.response(200, "Success", model=api_key_model)
    def get(self) -> Response:
        """
        Authenticates a user based on provided credentials and generates an API key.

        Reads the 'email' and 'password' from the JSON body of the request, validates the user,
        and if successful, generates and returns a new API key.

        If the email and password match a row in the database, a new API key is created using uuid.uuid4().hex, updated in for the matching user in the users table, and the API key is sent to the user.

        Returns:
        - dict: A dictionary containing the generated API key, or None if an error occurs.
        """
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        with self.setup_database_client() as db_client:
            response = get_api_key_for_user(db_client, email, password)
        return response
