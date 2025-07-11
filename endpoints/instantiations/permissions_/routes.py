from http import HTTPStatus

from flask import Response, request

from middleware.schema_and_dto.dynamic.schema.documentation_construction import (
    get_restx_param_documentation,
)
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.security.auth.info.instantiations import (
    WRITE_ONLY_AUTH_INFO,
)
from middleware.security.auth.info.base import AuthenticationInfo
from middleware.decorators.endpoint_info import endpoint_info
from middleware.enums import PermissionsEnum, AccessTypeEnum
from middleware.primary_resource_logic.permissions import (
    manage_user_permissions,
    update_permissions_wrapper,
    PermissionsRequestDTO,
    PermissionsPutRequestSchema,
)
from endpoints.psycopg_resource import PsycopgResource
from endpoints.schema_config.enums import SchemaConfigs
from endpoints._helpers.parser import add_jwt_header_arg
from endpoints._helpers.response_info import ResponseInfo
from utilities.namespace import AppNamespaces, create_namespace
from middleware.schema_and_dto.non_dto_dataclasses import SchemaPopulateParameters

namespace_permissions = create_namespace(namespace_attributes=AppNamespaces.PERMISSIONS)

doc_info = get_restx_param_documentation(
    namespace=namespace_permissions,
    schema=PermissionsPutRequestSchema,
    model_name="PermissionRequest",
)

permission_model = doc_info.model
all_routes_parser = doc_info.parser
add_jwt_header_arg(all_routes_parser)


@namespace_permissions.route("")
class Permissions(PsycopgResource):
    """
    Provides a resource for retrieving permissions for a user.
    """

    @endpoint_info(
        namespace=namespace_permissions,
        auth_info=AuthenticationInfo(
            allowed_access_methods=[AccessTypeEnum.JWT],
            restrict_to_permissions=[PermissionsEnum.READ_ALL_USER_INFO],
        ),
        response_info=ResponseInfo(success_message="Returns a user's permissions."),
        description="Retrieves a user's permissions.",
        schema_config=SchemaConfigs.PERMISSIONS_GET,
    )
    def get(self, access_info: AccessInfoPrimary) -> Response:
        """
        Retrieves a user's permissions.
        :return:
        """
        return self.run_endpoint(
            manage_user_permissions,
            user_email=request.args.get("user_email"),
            method="get_user_permissions",
        )

    @endpoint_info(
        namespace=namespace_permissions,
        auth_info=WRITE_ONLY_AUTH_INFO,
        schema_config=SchemaConfigs.PERMISSIONS_PUT,
        response_info=ResponseInfo(
            response_dictionary={
                HTTPStatus.OK.value: "OK; Permissions added",
                HTTPStatus.INTERNAL_SERVER_ERROR.value: "Internal server error",
                HTTPStatus.CONFLICT.value: "Permission already exists for user (if adding) or does not exist for user (if removing)",
                HTTPStatus.BAD_REQUEST.value: "Missing or bad query parameter",
            }
        ),
        description="Adds or removes a permission for a user.",
    )
    def put(self, access_info: AccessInfoPrimary) -> Response:
        """
        Adds or removes a permission for a user.
        :return:
        """
        return self.run_endpoint(
            wrapper_function=update_permissions_wrapper,
            schema_populate_parameters=SchemaPopulateParameters(
                schema=PermissionsPutRequestSchema(),
                dto_class=PermissionsRequestDTO,
            ),
        )
