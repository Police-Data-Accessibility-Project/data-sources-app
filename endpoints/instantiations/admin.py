from flask import Response

from endpoints.schema_config.instantiations.admin.users.by_id.delete import (
    AdminUsersByIDDeleteEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.admin.users.by_id.put import (
    AdminUsersByIDPutEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.admin.users.post import (
    AdminUsersPostEndpointSchemaConfig,
)
from middleware.access_logic import (
    AccessInfoPrimary,
)
from middleware.authentication_info import READ_USER_AUTH_INFO, WRITE_USER_AUTH_INFO
from middleware.decorators.decorators import (
    endpoint_info,
)
from middleware.primary_resource_logic.admin import (
    get_users_admin,
    create_admin_user,
    update_user_password,
    delete_user,
)
from middleware.schema_and_dto.populate_parameters import (
    GET_MANY_SCHEMA_POPULATE_PARAMETERS,
)
from endpoints.psycopg_resource import PsycopgResource
from endpoints.schema_config.enums import SchemaConfigs
from endpoints._helpers.response_info import ResponseInfo
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
        """
        Creates a new user.
        """
        return self.run_endpoint(
            wrapper_function=create_admin_user,
            schema_populate_parameters=AdminUsersPostEndpointSchemaConfig.get_schema_populate_parameters(),
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
        """
        Updates a user's password
        """
        return self.run_endpoint(
            update_user_password,
            schema_populate_parameters=AdminUsersByIDPutEndpointSchemaConfig.get_schema_populate_parameters(),
            user_id=int(resource_id),
        )

    @endpoint_info(
        namespace=namespace_admin,
        auth_info=WRITE_USER_AUTH_INFO,
        schema_config=SchemaConfigs.ADMIN_USERS_BY_ID_DELETE,
        response_info=ResponseInfo(success_message="Admin user deleted."),
        description="Deletes an admin user",
    )
    def delete(self, resource_id: str, access_info: AccessInfoPrimary) -> Response:
        """
        Deletes a user
        """
        return self.run_endpoint(
            wrapper_function=delete_user,
            schema_populate_parameters=AdminUsersByIDDeleteEndpointSchemaConfig.get_schema_populate_parameters(),
        )
