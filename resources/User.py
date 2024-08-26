from http import HTTPStatus

from flask import request
from flask_restx import fields

from middleware.reset_token_queries import set_user_password
from middleware.user_queries import user_post_results, UserRequest
from middleware.decorators import api_key_required
from typing import Dict, Any

from resources.resource_helpers import add_api_key_header_arg, create_user_model
from utilities.namespace import create_namespace
from resources.PsycopgResource import PsycopgResource, handle_exceptions
from utilities.populate_dto_with_request_content import (
    populate_dto_with_request_content,
    SourceMappingEnum,
)

namespace_user = create_namespace()

# Define the user model for request parsing and validation
user_model = create_user_model(namespace_user)

authorization_parser = namespace_user.parser()
add_api_key_header_arg(authorization_parser)


@namespace_user.route("/user")
class User(PsycopgResource):
    """
    A resource for user management, allowing new users to sign up and existing users to update their passwords.
    """

    @handle_exceptions
    @namespace_user.expect(user_model)
    @namespace_user.response(201, "Success: User created")
    @namespace_user.response(500, "Error: Internal server error")
    @namespace_user.response(401, "Error: Unauthorized login failed.")
    def post(self) -> Dict[str, Any]:
        """
        Allows a new user to sign up by providing an email and password.

        The email and a hashed password are stored in the database. Upon successful registration,
        a message is returned to the user.

        Returns:
        - A dictionary containing a success message or an error message if the operation fails.
        """
        dto = populate_dto_with_request_content(
            dto_class=UserRequest,
            source=SourceMappingEnum.JSON,
        )
        with self.setup_database_client() as db_client:
            user_post_results(db_client, dto)

        return {"message": "Successfully added user"}

    # Endpoint for updating a user's password
    @handle_exceptions
    @namespace_user.expect(authorization_parser, user_model)
    @namespace_user.response(201, "Success: User password successfully updated")
    @namespace_user.response(500, "Error: Internal server error")
    @namespace_user.doc(
        description="Update user password.",
    )
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
