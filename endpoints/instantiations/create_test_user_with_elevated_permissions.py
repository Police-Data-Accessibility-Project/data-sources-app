"""
This is a resource for a /create-test-user-with-elevated-permissions endpoint.
This resource test user with elevated permissions
Purely for the sake of testing.
It is designed to be quick and dirty and to not follow the same coding conventions
as every other resource. It has no tests, and the environment variable is not
mentioned in the readme.

It is designed to be removed or ignored in production.
The endpoint requires a DEVELOPMENT_PASSWORD environment variable which,
if not set, causes all attempts to generate a test user to fail.
"""

import uuid
from http import HTTPStatus

from flask import request
from flask_restx import fields, abort
from werkzeug.exceptions import Unauthorized, InternalServerError

from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.enums import PermissionsEnum, AccessTypeEnum
from middleware.primary_resource_logic.api_key import create_api_key_for_user
from middleware.primary_resource_logic.user_queries import (
    user_post_results,
    UserRequestDTO,
)
from middleware.util.env import get_env_variable
from endpoints.psycopg_resource import PsycopgResource
from utilities.namespace import AppNamespaces, create_namespace

namespace_create_test_user = create_namespace(namespace_attributes=AppNamespaces.DEV)

yolo_model = namespace_create_test_user.model(
    name="TestUserInformation",
    model={
        "email": fields.String(required=True),
        "password": fields.String(required=True),
        "api_key": fields.String(required=True),
    },
)

dev_password_model = namespace_create_test_user.model(
    name="DevPassword",
    model={
        "dev_password": fields.String(
            required=True,
            description="Development password, valid only in stage and test environments, to generate a test user with elevated permissions.",
        ),
    },
)


def check_dev_password(dev_password: str) -> bool:

    try:
        expected_dev_password = get_env_variable("DEVELOPMENT_PASSWORD")
        if dev_password != expected_dev_password:
            raise Unauthorized("Incorrect development password.")
    except ValueError:
        raise InternalServerError(
            "Server DEVELOPMENT_PASSWORD not set. Please set the DEVELOPMENT_PASSWORD as an environment variable."
        )


@namespace_create_test_user.route("/create-test-user-with-elevated-permissions")
class CreateTestUserWithElevatedPermissions(PsycopgResource):

    @namespace_create_test_user.response(HTTPStatus.OK, "Success", yolo_model)
    @namespace_create_test_user.response(
        HTTPStatus.INTERNAL_SERVER_ERROR,
        "Internal server error OR Server DEVELOPMENT_PASSWORD not set.",
    )
    @namespace_create_test_user.response(
        HTTPStatus.UNAUTHORIZED, "Incorrect development password"
    )
    @namespace_create_test_user.doc(
        description="Creates a test user with elevated permissions. Requires a development which matches the DEVELOPMENT_PASSWORD environment variable."
    )
    @namespace_create_test_user.expect(dev_password_model)
    def post(self):
        """
        Creates a test user with elevated permissions
        :return:
        """
        data = request.get_json()
        dev_password = data.get("dev_password")
        check_dev_password(dev_password=dev_password)
        auto_user_email = uuid.uuid4().hex
        auto_user_password = uuid.uuid4().hex
        dto = UserRequestDTO(
            email=auto_user_email,
            password=auto_user_password,
        )
        with self.setup_database_client() as db_client:
            user_post_results(db_client=db_client, dto=dto)
            for permission in [
                PermissionsEnum.READ_ALL_USER_INFO,
                PermissionsEnum.DB_WRITE,
                PermissionsEnum.NOTIFICATIONS,
                PermissionsEnum.SOURCE_COLLECTOR,
            ]:
                db_client.add_user_permission(
                    user_id=db_client.get_user_id(email=auto_user_email),
                    permission=permission,
                )
            access_info = AccessInfoPrimary(
                access_type=AccessTypeEnum.JWT,
                user_email=auto_user_email,
            )
            api_key = create_api_key_for_user(
                db_client=db_client, access_info=access_info
            ).json["api_key"]
        return {
            "email": auto_user_email,
            "password": auto_user_password,
            "api_key": api_key,
        }
