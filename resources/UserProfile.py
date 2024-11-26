from flask import Response

from middleware.access_logic import (
    AuthenticationInfo,
    AccessInfoPrimary,
    STANDARD_JWT_AUTH_INFO,
)
from middleware.decorators import endpoint_info, endpoint_info_2
from middleware.enums import AccessTypeEnum
from middleware.primary_resource_logic.reset_token_queries import (
    change_password_wrapper,
)
from middleware.primary_resource_logic.user_profile import (
    get_owner_data_requests_wrapper,
    get_user_recent_searches,
    get_user_by_id_wrapper,
)
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    GetManyRequestsBaseSchema,
    GET_MANY_SCHEMA_POPULATE_PARAMETERS,
)
from middleware.schema_and_dto_logic.dynamic_logic.dynamic_schema_documentation_construction import (
    get_restx_param_documentation,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.data_requests_advanced_schemas import (
    GetManyDataRequestsResponseSchema,
)
from resources.PsycopgResource import PsycopgResource
from resources.endpoint_schema_config import SchemaConfigs
from resources.resource_helpers import create_response_dictionary, ResponseInfo
from utilities.namespace import AppNamespaces, create_namespace

namespace_user = create_namespace(AppNamespaces.USER)

DATA_REQUESTS_PARTIAL_ENDPOINT = "data-requests"
USER_PROFILE_DATA_REQUEST_ENDPOINT_FULL = f"/api/user/{DATA_REQUESTS_PARTIAL_ENDPOINT}"

user_data_requests_model = get_restx_param_documentation(
    namespace=namespace_user,
    schema=GetManyDataRequestsResponseSchema(exclude=["data.internal_notes"]),
    model_name="GetManyBaseSchema",
).model


@namespace_user.route("/<user_id>/update-password")
class UserUpdatePassword(PsycopgResource):

    @endpoint_info_2(
        namespace=namespace_user,
        auth_info=STANDARD_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.USER_PUT,
        response_info=ResponseInfo(
            response_dictionary={
                200: "Success: User password successfully updated",
                500: "Error: Internal server error",
            }
        ),
    )
    def post(self, access_info: AccessInfoPrimary, user_id: int) -> Response:
        """
        Allows an existing user to update their password.

        The user's new password is hashed and updated in the database based on their email.
        Upon successful password update, a message is returned to the user.

        Returns:
        - A dictionary containing a success message or an error message if the operation fails.
        """
        return self.run_endpoint(
            wrapper_function=change_password_wrapper,
            schema_populate_parameters=SchemaConfigs.USER_PUT.value.get_schema_populate_parameters(),
            access_info=access_info,
            user_id=user_id,
        )


@namespace_user.route("/<user_id>")
class UserByID(PsycopgResource):
    @endpoint_info_2(
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
        auth_info=AuthenticationInfo(
            allowed_access_methods=[AccessTypeEnum.JWT],
        ),
        input_schema=GetManyRequestsBaseSchema(),
        description="Get data requests created by user",
        responses=create_response_dictionary(
            success_message="Returns a paginated list of data requests.",
            success_model=user_data_requests_model,
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
    @endpoint_info_2(
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
