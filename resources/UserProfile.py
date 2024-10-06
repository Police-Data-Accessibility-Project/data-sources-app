from flask import Response

from middleware.access_logic import GET_AUTH_INFO, AuthenticationInfo, AccessInfo
from middleware.decorators import endpoint_info
from middleware.enums import AccessTypeEnum
from middleware.primary_resource_logic.user_profile import (
    get_owner_data_requests_wrapper,
)
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    GetManyBaseSchema,
    GET_MANY_SCHEMA_POPULATE_PARAMETERS,
)
from middleware.schema_and_dto_logic.dynamic_schema_documentation_construction import (
    get_restx_param_documentation,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.data_requests import (
    GetManyDataRequestsSchema,
)
from resources.PsycopgResource import PsycopgResource
from resources.resource_helpers import create_response_dictionary
from utilities.namespace import AppNamespaces, create_namespace

namespace_user = create_namespace(AppNamespaces.USER)

DATA_REQUESTS_PARTIAL_ENDPOINT = "data-requests"
USER_PROFILE_DATA_REQUEST_ENDPOINT_FULL = f"/api/user/{DATA_REQUESTS_PARTIAL_ENDPOINT}"

user_data_requests_model = get_restx_param_documentation(
    namespace=namespace_user,
    schema=GetManyDataRequestsSchema(exclude=["data.internal_notes"]),
    model_name="GetManyBaseSchema",
).model


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
        input_schema=GetManyBaseSchema(),
        description="Get data requests created by user",
        responses=create_response_dictionary(
            success_message="Returns a paginated list of data requests.",
            success_model=user_data_requests_model,
        ),
    )
    def get(self, access_info: AccessInfo) -> Response:
        pass
        return self.run_endpoint(
            wrapper_function=get_owner_data_requests_wrapper,
            schema_populate_parameters=GET_MANY_SCHEMA_POPULATE_PARAMETERS,
            access_info=access_info,
        )
