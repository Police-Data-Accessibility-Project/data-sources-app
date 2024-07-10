from http import HTTPStatus

from werkzeug.security import generate_password_hash
from flask import request

from middleware.reset_token_queries import set_user_password
from middleware.user_queries import user_post_results
from middleware.security import api_required
from typing import Dict, Any

from resources.PsycopgResource import PsycopgResource, handle_exceptions


class User(PsycopgResource):
    """
    A resource for user management, allowing new users to sign up and existing users to update their passwords.
    """

    @handle_exceptions
    def post(self) -> Dict[str, Any]:
        """
        Allows a new user to sign up by providing an email and password.

        The email and a hashed password are stored in the database. Upon successful registration,
        a message is returned to the user.

        Returns:
        - A dictionary containing a success message or an error message if the operation fails.
        """
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        with self.setup_database_client() as db_client:
            user_post_results(db_client, email, password)

        return {"message": "Successfully added user"}

    # Endpoint for updating a user's password
    @handle_exceptions
    @api_required
    def put(self) -> Dict[str, Any]:
        """
        Allows an existing user to update their password.

        The user's new password is hashed and updated in the database based on their email.
        Upon successful password update, a message is returned to the user.

        Returns:
        - A dictionary containing a success message or an error message if the operation fails.
        """
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        with self.setup_database_client() as db_client:
            set_user_password(db_client, email, password)
        return {"message": "Successfully updated password"}, HTTPStatus.OK
