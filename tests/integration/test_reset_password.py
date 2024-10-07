"""Integration tests for /reset-password endpoint."""

from http import HTTPStatus
import uuid

import psycopg

from tests.conftest import dev_db_client, flask_client_with_db
from tests.helper_scripts.helper_functions import (
    create_test_user_api,
    request_reset_password_api,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request
from tests.helper_scripts.simple_result_validators import check_response_status


def test_reset_password_post(flask_client_with_db, dev_db_client, mocker):
    """
    Test that POST call to /reset-password endpoint successfully resets the user's password, and verifies the new password digest is distinct from the old one in the database
    """

    user_info = create_test_user_api(flask_client_with_db)
    # User should be able to log in with the old password
    run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="post",
        endpoint="/api/login",
        json={"email": user_info.email, "password": user_info.password},
    )

    old_password_digest = dev_db_client.get_user_info(user_info.email).password_digest

    token = request_reset_password_api(flask_client_with_db, mocker, user_info)
    new_password = str(uuid.uuid4())
    run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="post",
        endpoint="/api/reset-password",
        json={"email": user_info.email, "token": token, "password": new_password},
    )
    new_password_digest = dev_db_client.get_user_info(user_info.email).password_digest
    assert (
        new_password_digest != old_password_digest
    ), "Old and new password digests should be distinct"

    # User should not be able to log in with the old password
    run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="post",
        endpoint="/api/login",
        json={"email": user_info.email, "password": user_info.password},
        expected_response_status=HTTPStatus.UNAUTHORIZED,
    )

    # User should be able to login with the new password
    run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="post",
        endpoint="/api/login",
        json={"email": user_info.email, "password": new_password},
    )


def test_reset_password_user_cant_reset_another_users_password(
    flask_client_with_db, dev_db_client, mocker
):
    user_info_1 = create_test_user_api(flask_client_with_db)
    user_info_2 = create_test_user_api(flask_client_with_db)
    password_digest_user_2 = dev_db_client.get_user_info(
        user_info_2.email
    ).password_digest
    password_digest_user_1 = dev_db_client.get_user_info(
        user_info_1.email
    ).password_digest
    token = request_reset_password_api(flask_client_with_db, mocker, user_info_1)
    new_password = str(uuid.uuid4())

    # Should get a bad request if user tries to reset another user's password
    run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="post",
        endpoint="/api/reset-password",
        json={"email": user_info_2.email, "token": token, "password": new_password},
        expected_response_status=HTTPStatus.BAD_REQUEST,
    )

    # Neither user should be able to login with the new password
    run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="post",
        endpoint="/api/login",
        json={"email": user_info_2.email, "password": new_password},
        expected_response_status=HTTPStatus.UNAUTHORIZED,
    )

    run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="post",
        endpoint="/api/login",
        json={"email": user_info_1.email, "password": new_password},
        expected_response_status=HTTPStatus.UNAUTHORIZED,
    )
