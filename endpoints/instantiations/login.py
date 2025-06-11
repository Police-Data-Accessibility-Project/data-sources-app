from flask import Response

from config import limiter
from endpoints.schema_config.instantiations.auth.login import LoginEndpointSchemaConfig
from middleware.access_logic import AccessInfoPrimary
from middleware.authentication_info import NO_AUTH_INFO
from middleware.decorators.decorators import endpoint_info
from middleware.primary_resource_logic.login_queries import try_logging_in
from endpoints.schema_config.enums import SchemaConfigs
from endpoints._helpers.response_info import ResponseInfo
from utilities.namespace import create_namespace, AppNamespaces

from endpoints.psycopg_resource import PsycopgResource

namespace_login = create_namespace(AppNamespaces.AUTH)


@namespace_login.route("/login")
class Login(PsycopgResource):
    """
    A resource for authenticating users. Allows users to log in using their email and password.
    """

    @endpoint_info(
        namespace=namespace_login,
        auth_info=NO_AUTH_INFO,
        description="Allows a user to log in. If successful, returns a session token.",
        response_info=ResponseInfo(success_message="User logged in."),
        schema_config=SchemaConfigs.LOGIN_POST,
    )
    @limiter.limit("5 per minute")
    def post(self, access_info: AccessInfoPrimary) -> Response:
        """
        Processes the login request. Validates user credentials against the stored hashed password and,
        if successful, generates a session token for the user.

        Returns:
        - A dictionary containing a message of success or failure, and the session token if successful.
        """
        return self.run_endpoint(
            wrapper_function=try_logging_in,
            schema_populate_parameters=LoginEndpointSchemaConfig.get_schema_populate_parameters(),
        )
