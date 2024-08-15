"""
This is a resource for a /yolo endpoint.
The /yolo endpoint is a resource that creates a test user with elevated permissions
Purely for the sake of testing.
It is designed to be quick and dirty and to not follow the same coding conventions
as every other resource. It has no tests, and the environment variable is not
mentioned in the readme.

It is designed to be removed or ignored in production.
The endpoint requires a YASSWORD environment variable which,
if not set, causes all attempts to generate a test user to fail.
"""

import uuid
from http import HTTPStatus

from flask import request
from flask_restx import fields, abort

from middleware.enums import PermissionsEnum
from middleware.login_queries import get_api_key_for_user
from middleware.user_queries import user_post_results
from middleware.util import get_env_variable
from resources.PsycopgResource import PsycopgResource
from utilities.namespace import AppNamespaces, create_namespace

namespace_yolo = create_namespace(namespace_attributes=AppNamespaces.YOLO)

yolo_model = namespace_yolo.model(
    name="Yolo",
    model={
        "email": fields.String(required=True),
        "password": fields.String(required=True),
        "api_key": fields.String(required=True),
    },
)

yassword_model = namespace_yolo.model(
    name="Yassword",
    model={
        "yassword": fields.String(required=True),
    },
)


def check_yassword(yassword: str) -> bool:

    try:
        expected_yassword = get_env_variable("YASSWORD")
        if yassword != expected_yassword:
            abort(HTTPStatus.UNAUTHORIZED, message="Incorrect yassword")
    except ValueError:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, message="Server YASSWORD not set. Please set the YASSWORD as an environment variable.")


@namespace_yolo.route("/yolo")
class Yolo(PsycopgResource):

    @namespace_yolo.response(HTTPStatus.OK, "Success", yolo_model)
    @namespace_yolo.response(
        HTTPStatus.INTERNAL_SERVER_ERROR,
        "Internal server error OR Server YASSWORD not set.",
    )
    @namespace_yolo.response(HTTPStatus.UNAUTHORIZED, "Incorrect yassword")
    @namespace_yolo.doc(
        description="Creates a test user with elevated permissions. Requires a yassword."
    )
    @namespace_yolo.expect(yassword_model)
    def post(self):
        """
        Creates a test user with elevated permissions
        :return:
        """
        data = request.get_json()
        yassword = data.get("yassword")
        check_yassword(yassword=yassword)
        auto_user_email = uuid.uuid4().hex
        auto_user_password = uuid.uuid4().hex
        with self.setup_database_client() as db_client:
            user_post_results(
                db_client=db_client,
                email=auto_user_email,
                password=auto_user_password,
            )
            for permission in [
                PermissionsEnum.READ_ALL_USER_INFO,
                PermissionsEnum.DB_WRITE,
            ]:
                db_client.add_user_permission(
                    user_email=auto_user_email,
                    permission=permission,
                )
            api_key = get_api_key_for_user(
                db_client=db_client,
                email=auto_user_email,
                password=auto_user_password,
            ).json["api_key"]
        return {
            "email": auto_user_email,
            "password": auto_user_password,
            "api_key": api_key,
        }
