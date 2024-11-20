from flask import Response

from config import limiter
from middleware.access_logic import NO_AUTH_INFO, AccessInfo
from middleware.decorators import endpoint_info_2
from middleware.primary_resource_logic.login_queries import try_logging_in
from resources.endpoint_schema_config import SchemaConfigs
from resources.resource_helpers import create_jwt_tokens_model, ResponseInfo
from middleware.schema_and_dto_logic.dynamic_logic.model_helpers_with_schemas import (
    create_user_model,
)
from utilities.namespace import create_namespace

from resources.PsycopgResource import PsycopgResource, handle_exceptions

namespace_login = create_namespace()
user_model = create_user_model(namespace_login)
jwt_tokens_model = create_jwt_tokens_model(namespace_login)


@namespace_login.route("/login")
class Login(PsycopgResource):
    """
    A resource for authenticating users. Allows users to log in using their email and password.
    """

    @endpoint_info_2(
        namespace=namespace_login,
        auth_info=NO_AUTH_INFO,
        description="Allows a user to log in. If successful, returns a session token.",
        response_info=ResponseInfo(success_message="User logged in."),
        schema_config=SchemaConfigs.LOGIN_POST,
    )
    @limiter.limit("5 per minute")
    def post(self, access_info: AccessInfo) -> Response:
        """
        Processes the login request. Validates user credentials against the stored hashed password and,
        if successful, generates a session token for the user.

        Returns:
        - A dictionary containing a message of success or failure, and the session token if successful.
        """
        return self.run_endpoint(
            wrapper_function=try_logging_in,
            schema_populate_parameters=SchemaConfigs.LOGIN_POST.value.get_schema_populate_parameters(),
        )
