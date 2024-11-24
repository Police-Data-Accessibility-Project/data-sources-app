from http import HTTPStatus

from flask import Response

from middleware.primary_resource_logic.reset_token_queries import set_user_password
from middleware.primary_resource_logic.user_queries import (
    user_post_results,
    UserRequestDTO,
    UserRequestSchema,
)
from typing import Dict, Any

from middleware.schema_and_dto_logic.non_dto_dataclasses import SchemaPopulateParameters
from resources.resource_helpers import add_api_key_header_arg
from middleware.schema_and_dto_logic.dynamic_logic.model_helpers_with_schemas import (
    create_user_model,
)
from utilities.namespace import create_namespace
from resources.PsycopgResource import PsycopgResource, handle_exceptions
from middleware.schema_and_dto_logic.dynamic_logic.dynamic_schema_request_content_population import (
    populate_schema_with_request_content,
)

namespace_user_old = create_namespace()

# Define the user model for request parsing and validation
user_model = create_user_model(namespace_user_old)

authorization_parser = namespace_user_old.parser()
add_api_key_header_arg(authorization_parser)


@namespace_user_old.route("/user")
class User(PsycopgResource):
    """
    A resource for user management, allowing new users to sign up and existing users to update their passwords.
    """

    @handle_exceptions
    @namespace_user_old.expect(user_model)
    @namespace_user_old.response(HTTPStatus.OK, "Success: User created")
    @namespace_user_old.response(500, "Error: Internal server error")
    def post(self) -> Response:
        """
        Allows a new user to sign up by providing an email and password.

        The email and a hashed password are stored in the database. Upon successful registration,
        a message is returned to the user.

        Returns:
        - A dictionary containing a success message or an error message if the operation fails.
        """
        return self.run_endpoint(
            wrapper_function=user_post_results,
            schema_populate_parameters=SchemaPopulateParameters(
                schema=UserRequestSchema(),
                dto_class=UserRequestDTO,
            ),
        )

    # Endpoint for updating a user's password
    @handle_exceptions
    @namespace_user_old.expect(authorization_parser, user_model)
    @namespace_user_old.response(201, "Success: User password successfully updated")
    @namespace_user_old.response(500, "Error: Internal server error")
    @namespace_user_old.doc(
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
        dto = populate_schema_with_request_content(
            schema=UserRequestSchema(),
            dto_class=UserRequestDTO,
        )
        with self.setup_database_client() as db_client:
            set_user_password(
                db_client=db_client,
                user_id=db_client.get_user_info(dto.email).id,
                password=dto.password,
            )
        return {"message": "Successfully updated password"}, HTTPStatus.OK
