from http import HTTPStatus

from flask import Response

from middleware.access_logic import STANDARD_JWT_AUTH_INFO, AccessInfoPrimary
from middleware.decorators import endpoint_info_2
from middleware.primary_resource_logic.reset_token_queries import (
    set_user_password,
    change_password_wrapper,
)
from middleware.primary_resource_logic.user_queries import (
    user_post_results,
    UserRequestDTO,
    UserRequestSchema,
)
from typing import Dict, Any

from middleware.schema_and_dto_logic.non_dto_dataclasses import SchemaPopulateParameters
from resources.endpoint_schema_config import SchemaConfigs
from resources.resource_helpers import ResponseInfo
from middleware.schema_and_dto_logic.dynamic_logic.model_helpers_with_schemas import (
    create_user_model,
)
from utilities.namespace import create_namespace, AppNamespaces
from resources.PsycopgResource import PsycopgResource, handle_exceptions
from middleware.schema_and_dto_logic.dynamic_logic.dynamic_schema_request_content_population import (
    populate_schema_with_request_content,
)

namespace_user_old = create_namespace(AppNamespaces.USER)

# Define the user model for request parsing and validation
user_model = create_user_model(namespace_user_old)


@namespace_user_old.route("")
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
