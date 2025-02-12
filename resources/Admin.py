from flask import Response

from config import limiter
from middleware.access_logic import (
    AccessInfoPrimary,
    WRITE_USER_AUTH_INFO,
    READ_USER_AUTH_INFO,
)
from middleware.decorators import (
    endpoint_info,
)
from middleware.primary_resource_logic.admin import (
    get_users_admin,
    create_admin_user,
    update_user_password,
)
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    GET_MANY_SCHEMA_POPULATE_PARAMETERS,
)
from resources.PsycopgResource import PsycopgResource
from resources.endpoint_schema_config import SchemaConfigs
from resources.resource_helpers import (
    ResponseInfo,
)
from utilities.namespace import create_namespace, AppNamespaces

namespace_admin = create_namespace(
    AppNamespaces.ADMIN,
)


@namespace_admin.route("/users", methods=["GET", "POST"])
class AdminUsersByPage(PsycopgResource):

    @endpoint_info(
        namespace=namespace_admin,
        auth_info=READ_USER_AUTH_INFO,
        schema_config=SchemaConfigs.ADMIN_USERS_GET_MANY,
        response_info=ResponseInfo(
            success_message="Returns a paginated list of admin users."
        ),
    )
    def get(self, access_info: AccessInfoPrimary) -> Response:
        """
        Retrieves a paginated list of users from the database.

        Returns:
        - dict: A dictionary containing the count of returned admin users and their data.
        """
        return self.run_endpoint(
            wrapper_function=get_users_admin,
            schema_populate_parameters=GET_MANY_SCHEMA_POPULATE_PARAMETERS,
        )

    @endpoint_info(
        namespace=namespace_admin,
        auth_info=WRITE_USER_AUTH_INFO,
        schema_config=SchemaConfigs.ADMIN_USERS_POST,
        response_info=ResponseInfo(
            success_message="Returns the id of the newly created user."
        ),
    )
    def post(self, access_info: AccessInfoPrimary):
        return self.run_endpoint(
            wrapper_function=create_admin_user,
            schema_populate_parameters=SchemaConfigs.ADMIN_USERS_POST.value.get_schema_populate_parameters(),
        )


@namespace_admin.route("/users/<resource_id>", methods=["GET", "PUT", "DELETE"])
class AdminUsersByID(PsycopgResource):

    @endpoint_info(
        namespace=namespace_admin,
        auth_info=WRITE_USER_AUTH_INFO,
        schema_config=SchemaConfigs.ADMIN_USERS_BY_ID_PUT,
        response_info=ResponseInfo(success_message="Admin user updated."),
        description="Updates an admin user",
    )
    def put(self, resource_id: str, access_info: AccessInfoPrimary) -> Response:
        return self.run_endpoint(
            update_user_password,
            schema_populate_parameters=SchemaConfigs.ADMIN_USERS_BY_ID_PUT.value.get_schema_populate_parameters(),
            user_id=int(resource_id),
        )
