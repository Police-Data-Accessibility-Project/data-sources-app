from http import HTTPStatus

from flask import Response, request

from middleware.decorators import permissions_required
from middleware.enums import PermissionsEnum
from middleware.primary_resource_logic.permissions_logic import (
    manage_user_permissions,
    update_permissions_wrapper,
    PermissionsRequest,
    PermissionsRequestSchema,
)
from resources.PsycopgResource import handle_exceptions, PsycopgResource
from resources.resource_helpers import add_jwt_header_arg
from utilities.namespace import AppNamespaces, create_namespace
from middleware.schema_and_dto_logic.dynamic_logic.dynamic_schema_documentation_construction import (
    get_restx_param_documentation,
)
from middleware.schema_and_dto_logic.non_dto_dataclasses import SchemaPopulateParameters

namespace_permissions = create_namespace(namespace_attributes=AppNamespaces.AUTH)

doc_info = get_restx_param_documentation(
    namespace=namespace_permissions,
    schema=PermissionsRequestSchema,
    model_name="PermissionRequest",
)

permission_model = doc_info.model
all_routes_parser = doc_info.parser
add_jwt_header_arg(all_routes_parser)


@namespace_permissions.route("/permissions")
class Permissions(PsycopgResource):
    """
    Provides a resource for retrieving permissions for a user.
    """

    @namespace_permissions.expect(all_routes_parser)
    @namespace_permissions.response(HTTPStatus.OK.value, "OK; Permissions retrieved")
    @namespace_permissions.response(
        HTTPStatus.INTERNAL_SERVER_ERROR.value, "Internal server error"
    )
    @namespace_permissions.doc(
        description="Retrieves a user's permissions.",
    )
    @permissions_required(PermissionsEnum.READ_ALL_USER_INFO)
    def get(self) -> Response:
        """
        Retrieves a user's permissions.
        :return:
        """
        return self.run_endpoint(
            manage_user_permissions,
            user_email=request.args.get("user_email"),
            method="get_user_permissions",
        )

    @handle_exceptions
    @namespace_permissions.expect(all_routes_parser, permission_model)
    @namespace_permissions.response(HTTPStatus.OK.value, "OK; Permissions added")
    @namespace_permissions.response(
        HTTPStatus.INTERNAL_SERVER_ERROR.value, "Internal server error"
    )
    @namespace_permissions.response(
        HTTPStatus.CONFLICT.value,
        "Permission already exists for user (if adding) or does not exist for user (if removing)",
    )
    @namespace_permissions.response(
        HTTPStatus.BAD_REQUEST.value, "Missing or bad query parameter"
    )
    @namespace_permissions.doc(
        description="Adds or removes a permission for a user.",
    )
    @permissions_required(PermissionsEnum.DB_WRITE)
    def put(self) -> Response:
        """
        Adds or removes a permission for a user.
        :return:
        """
        return self.run_endpoint(
            wrapper_function=update_permissions_wrapper,
            schema_populate_parameters=SchemaPopulateParameters(
                schema=PermissionsRequestSchema(),
                dto_class=PermissionsRequest,
            ),
        )
