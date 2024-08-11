from http import HTTPStatus

from flask import Response, request
from flask_restx import fields

from middleware.decorators import api_key_required
from middleware.enums import PermissionsEnum, PermissionsActionEnum
from middleware.permissions_logic import (
    manage_user_permissions,
    update_permissions_wrapper,
)
from resources.PsycopgResource import handle_exceptions, PsycopgResource
from resources.resource_helpers import add_api_key_header_arg
from utilities.namespace import AppNamespaces, create_namespace

namespace_permissions = create_namespace(namespace_attributes=AppNamespaces.AUTH)

allowable_permissions_str = "Allowable permissions include: \n  * " + "\n  * ".join(
    PermissionsEnum.values()
)
allowable_actions_str = "Allowable actions include: \n  * " + "\n  * ".join(
    PermissionsActionEnum.values()
)
permission_model = namespace_permissions.model(
    "Permission",
    {
        "permission": fields.String(
            description=f"The permission to add or remove.\n {allowable_permissions_str}"
        ),
        "action": fields.String(
            description=f"The action to perform.\n {allowable_actions_str} ",
        ),
    },
)

all_routes_parser = namespace_permissions.parser()
add_api_key_header_arg(all_routes_parser)
all_routes_parser.add_argument(
    "user_email",
    type=str,
    location="query",
    required=True,
    help="The user for which to retrieve permissions.",
)


@namespace_permissions.route("/permissions")
class Permissions(PsycopgResource):
    """
    Provides a resource for retrieving permissions for a user.
    """

    @handle_exceptions
    @namespace_permissions.expect(all_routes_parser)
    @namespace_permissions.response(HTTPStatus.OK.value, "OK; Permissions retrieved")
    @namespace_permissions.response(
        HTTPStatus.INTERNAL_SERVER_ERROR.value, "Internal server error"
    )
    @namespace_permissions.doc(
        description="Retrieves a user's permissions.",
    )
    @api_key_required(PermissionsEnum.READ_ALL_USER_INFO)
    def get(self) -> Response:
        """
        Retrieves a user's permissions.
        :return:
        """
        user_email = request.args.get("user_email")
        with self.setup_database_client() as db_client:
            return manage_user_permissions(
                db_client=db_client,
                user_email=user_email,
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
    @api_key_required(PermissionsEnum.DB_WRITE)
    def put(self) -> Response:
        """
        Adds or removes a permission for a user.
        :return:
        """
        data = request.args
        json_data = request.get_json()
        with self.setup_database_client() as db_client:
            return update_permissions_wrapper(
                db_client=db_client,
                user_email=data.get("user_email"),
                action=json_data.get("action"),
                permission=json_data.get("permission"),
            )
