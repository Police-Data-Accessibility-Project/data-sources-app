"""Integration tests for /user endpoint."""

from http import HTTPStatus
import uuid

import pytest

from database_client.database_client import DatabaseClient
from tests.conftest import flask_client_with_db
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)
from tests.helper_scripts.constants import USERS_BASE_ENDPOINT
from tests.helper_scripts.helper_functions import (
    create_test_user_api,
    get_user_password_digest,
    create_test_user_setup,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request
from conftest import test_data_creator_flask, monkeysession


def test_user_post(flask_client_with_db):
    """
    Test that POST call to /user endpoint successfully creates a new user and verifies the user's email and password digest in the database
    """

    user_info = create_test_user_api(flask_client_with_db)
    db_client = DatabaseClient()
    rows = db_client.execute_raw_sql(
        f"SELECT email, password_digest FROM users WHERE email = %s", (user_info.email,)
    )

    assert len(rows) == 1, "One row should be returned by user query"
    email = rows[0]["email"]
    password_digest = rows[0]["password_digest"]
    assert user_info.email == email, "DB user email and original email do not match"
    assert (
        user_info.password != password_digest
    ), "DB user password digest should not match password"


def test_user_post_user_already_exists(
    test_data_creator_flask: TestDataCreatorFlask,
):
    """
    Test that POST call to /user endpoint fails if the user already exists
    """
    tdc = test_data_creator_flask

    tus = tdc.standard_user()
    data = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="post",
        endpoint=USERS_BASE_ENDPOINT,
        json={"email": tus.user_info.email, "password": "test"},
        expected_response_status=HTTPStatus.CONFLICT,
        expected_json_content={
            "message": f"User with email {tus.user_info.email} already exists."
        },
    )


def test_user_put(
    test_data_creator_flask: TestDataCreatorFlask,
):
    """
    Test that PUT call to /user endpoint successfully updates the user's password and verifies the new password hash is distinct from both the plain new password and the old password hash in the database
    """
    tdc = test_data_creator_flask

    tus = tdc.standard_user()
    old_password_hash = get_user_password_digest(tus.user_info)

    new_password = str(uuid.uuid4())

    def update_password(
        old_password: str,
        user_id: str = tus.user_info.user_id,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
    ):
        return tdc.request_validator.update_password(
            headers=tus.jwt_authorization_header,
            user_id=user_id,
            old_password=old_password,
            new_password=new_password,
            expected_response_status=expected_response_status,
        )

    # Try to update password with different user and fail
    tus_other = tdc.standard_user()
    update_password(
        old_password=tus_other.user_info.password,
        user_id=tus_other.user_info.user_id,
        expected_response_status=HTTPStatus.UNAUTHORIZED,
    )

    # Try to update password with incorrect old password and fail
    update_password(
        old_password="gibberish",
        expected_response_status=HTTPStatus.UNAUTHORIZED,
    )

    # Try to update password with correct old password and succeed
    response = update_password(
        old_password=tus.user_info.password,
    )

    new_password_hash = get_user_password_digest(tus.user_info)

    assert (
        new_password != new_password_hash
    ), "Password and password hash should be distinct after password update"
    assert (
        new_password_hash != old_password_hash
    ), "Password hashes should be different on update"
