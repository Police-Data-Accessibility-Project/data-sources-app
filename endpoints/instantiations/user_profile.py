from flask import Response

from endpoints.schema_config.instantiations.user.put import UserPutEndpointSchemaConfig
from middleware.access_logic import (
    AccessInfoPrimary,
)
from middleware.authentication_info import STANDARD_JWT_AUTH_INFO
from middleware.decorators.decorators import endpoint_info
from middleware.primary_resource_logic.reset_token_queries import (
    change_password_wrapper,
)
from middleware.primary_resource_logic.user_profile import (
    get_owner_data_requests_wrapper,
    get_user_recent_searches,
    get_user_by_id_wrapper,
)
from middleware.schema_and_dto.populate_parameters import (
    GET_MANY_SCHEMA_POPULATE_PARAMETERS,
)
from endpoints.psycopg_resource import PsycopgResource
from endpoints.schema_config.enums import SchemaConfigs
from endpoints._helpers.response_info import ResponseInfo
from utilities.namespace import AppNamespaces, create_namespace

namespace_user = create_namespace(AppNamespaces.USER)

DATA_REQUESTS_PARTIAL_ENDPOINT = "data-requests"
USER_PROFILE_DATA_REQUEST_ENDPOINT_FULL = f"/api/user/{DATA_REQUESTS_PARTIAL_ENDPOINT}"


@namespace_user.route("/update-password")
class UserUpdatePassword(PsycopgResource):

    @endpoint_info(
        namespace=namespace_user,
        auth_info=STANDARD_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.USER_PUT,
        response_info=ResponseInfo(
            success_message="Password successfully updated.",
        ),
    )
    def post(self, access_info: AccessInfoPrimary) -> Response:
        """
        Allows an existing user to update their password.

        The user's new password is hashed and updated in the database based on their email.
        Upon successful password update, a message is returned to the user.

        Returns:
        - A dictionary containing a success message or an error message if the operation fails.
        """
        return self.run_endpoint(
            wrapper_function=change_password_wrapper,
            schema_populate_parameters=UserPutEndpointSchemaConfig.get_schema_populate_parameters(),
            access_info=access_info,
        )


@namespace_user.route("/<user_id>")
class UserByID(PsycopgResource):
    @endpoint_info(
        namespace=namespace_user,
        auth_info=STANDARD_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.USER_PROFILE_GET,
        response_info=ResponseInfo(
            success_message="Returns the user profile.",
        ),
        description="Get user profile",
    )
    def get(self, user_id: int, access_info: AccessInfoPrimary) -> Response:
        return self.run_endpoint(
            wrapper_function=get_user_by_id_wrapper,
            user_id=int(user_id),
            access_info=access_info,
        )


@namespace_user.route(f"/{DATA_REQUESTS_PARTIAL_ENDPOINT}")
class UserDataRequests(PsycopgResource):
    """
    Resource for getting all data requests created by a user
    """

    @endpoint_info(
        namespace=namespace_user,
        auth_info=STANDARD_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.USER_PROFILE_DATA_REQUESTS_GET,
        response_info=ResponseInfo(
            success_message="Returns a paginated list of data requests.",
        ),
    )
    def get(self, access_info: AccessInfoPrimary) -> Response:
        return self.run_endpoint(
            wrapper_function=get_owner_data_requests_wrapper,
            schema_populate_parameters=GET_MANY_SCHEMA_POPULATE_PARAMETERS,
            access_info=access_info,
        )


@namespace_user.route("/recent-searches")
class UserRecentSearches(PsycopgResource):
    @endpoint_info(
        namespace=namespace_user,
        auth_info=STANDARD_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.USER_PROFILE_RECENT_SEARCHES,
        response_info=ResponseInfo(
            success_message="Returns up to 50 of the user's recent searches.",
        ),
        description="Get user's recent searches",
    )
    def get(self, access_info: AccessInfoPrimary) -> Response:
        return self.run_endpoint(
            wrapper_function=get_user_recent_searches,
            access_info=access_info,
        )
