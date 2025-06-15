from flask import Response

from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.security.auth.info.instantiations import STANDARD_JWT_AUTH_INFO
from middleware.decorators.endpoint_info import endpoint_info
from middleware.primary_resource_logic.api_key import create_api_key_for_user

from endpoints.schema_config.enums import SchemaConfigs
from endpoints._helpers.response_info import ResponseInfo
from utilities.namespace import create_namespace, AppNamespaces

from endpoints.psycopg_resource import PsycopgResource

namespace_api_key = create_namespace(namespace_attributes=AppNamespaces.AUTH)
API_KEY_ROUTE = "/api-key"


@namespace_api_key.route(API_KEY_ROUTE)
class ApiKeyResource(PsycopgResource):
    """Represents a resource for generating an API key for authenticated users."""

    @endpoint_info(
        namespace=namespace_api_key,
        auth_info=STANDARD_JWT_AUTH_INFO,
        description="Generates an API key for authenticated users.",
        response_info=ResponseInfo(
            success_message="OK. API key generated.",
        ),
        schema_config=SchemaConfigs.API_KEY_POST,
    )
    def post(self, access_info: AccessInfoPrimary) -> Response:
        """
        Authenticates a user based on provided credentials and generates an API key.

        Reads the 'email' and 'password' from the JSON body of the request, validates the user,
        and if successful, generates and returns a new API key.

        If the email and password match a row in the database, a new API key is created using uuid.uuid4().hex, updated in for the matching user in the users table, and the API key is sent to the user.

        Returns:
        - dict: A dictionary containing the generated API key, or None if an error occurs.
        """
        return self.run_endpoint(
            wrapper_function=create_api_key_for_user,
            access_info=access_info,
        )
