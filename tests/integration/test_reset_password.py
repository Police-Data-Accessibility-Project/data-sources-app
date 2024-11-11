"""Integration tests for /reset-password endpoint."""

from http import HTTPStatus
import uuid


from tests.conftest import dev_db_client
from tests.helper_scripts.common_test_data import TestDataCreatorFlask
from tests.helper_scripts.helper_functions import (
    request_reset_password_api,
)
from conftest import test_data_creator_flask, monkeysession

def test_reset_password_post(test_data_creator_flask: TestDataCreatorFlask, dev_db_client, mocker):
    """
    Test that POST call to /reset-password endpoint successfully resets the user's password, and verifies the new password digest is distinct from the old one in the database
    """
    tdc = test_data_creator_flask

    tus = tdc.standard_user()
    user_info = tus.user_info

    def login(
        password: str,
        expected_response_status: HTTPStatus = HTTPStatus.OK
    ):
        tdc.request_validator.post(
            endpoint="/api/login",
            json={"email": user_info.email, "password": password},
            expected_response_status=expected_response_status,
        )

    # User should be able to log in with the old password
    login(user_info.password)

    old_password_digest = dev_db_client.get_user_info(user_info.email).password_digest

    token = request_reset_password_api(tdc.flask_client, mocker, user_info)

    new_password = str(uuid.uuid4())
    tdc.request_validator.post(
        endpoint="/api/reset-password",
        json={"email": user_info.email, "token": token, "password": new_password},
    )
    new_password_digest = dev_db_client.get_user_info(user_info.email).password_digest
    assert (
        new_password_digest != old_password_digest
    ), "Old and new password digests should be distinct"

    # User should not be able to log in with the old password
    login(
        password=user_info.password,
        expected_response_status=HTTPStatus.UNAUTHORIZED
    )

    # User should be able to login with the new password
    login(
        password=new_password
    )


def test_reset_password_user_cant_reset_another_users_password(
    test_data_creator_flask: TestDataCreatorFlask, mocker
):
    tdc = test_data_creator_flask
    user_info_1 = tdc.standard_user().user_info
    user_info_2 = tdc.standard_user().user_info

    token = request_reset_password_api(tdc.flask_client, mocker, user_info_1)
    new_password = str(uuid.uuid4())

    # Should get a bad request if user tries to reset another user's password
    tdc.request_validator.post(
        endpoint="/api/reset-password",
        json={"email": user_info_2.email, "token": token, "password": new_password},
        expected_response_status=HTTPStatus.BAD_REQUEST,
    )

    def try_login(email):
        tdc.request_validator.post(
            endpoint="/api/login",
            json={"email": email, "password": new_password},
            expected_response_status=HTTPStatus.UNAUTHORIZED,
        )

    # Neither user should be able to login with the new password
    try_login(user_info_1.email)
    try_login(user_info_2.email)
