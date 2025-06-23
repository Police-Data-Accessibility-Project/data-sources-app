from flask import Response

from middleware.security.access_info.refresh import RefreshAccessInfo
from middleware.security.auth.info.base import AuthenticationInfo
from middleware.decorators.endpoint_info import endpoint_info
from middleware.enums import AccessTypeEnum
from middleware.primary_resource_logic.login_queries import (
    refresh_session,
)
from endpoints.schema_config.enums import SchemaConfigs
from endpoints._helpers.response_info import ResponseInfo

from utilities.namespace import create_namespace, AppNamespaces
from endpoints.psycopg_resource import PsycopgResource

namespace_refresh_session = create_namespace(AppNamespaces.AUTH)


@namespace_refresh_session.route("/refresh-session")
class RefreshSession(PsycopgResource):
    """
    Provides a resource for refreshing a user's session token.
    If the provided session token is valid and not expired, it is replaced with a new one.
    """

    @endpoint_info(
        namespace=namespace_refresh_session,
        auth_info=AuthenticationInfo(
            allowed_access_methods=[AccessTypeEnum.REFRESH_JWT],
        ),
        description="Allows a user to refresh their session token.",
        response_info=ResponseInfo(success_message="Session token refreshed."),
        schema_config=SchemaConfigs.REFRESH_SESSION,
    )
    def post(self, access_info: RefreshAccessInfo) -> Response:
        """
        Processes the session token refresh request. If the provided session token is valid,
        it generates a new session token, invalidates the old one, and returns the new token.

        Returns:
        - A dictionary containing a message of success or failure, and the new session token if successful.
        """

        return self.run_endpoint(
            wrapper_function=refresh_session,
            access_info=access_info,
        )
