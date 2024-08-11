"""Integration tests for /reset-password endpoint."""

from http import HTTPStatus
import uuid

import psycopg2
import sqlalchemy

from conftest import test_client, session
from tests.helper_scripts.helper_functions import (
    create_test_user_api,
    get_user_password_digest,
    request_reset_password_api,
    check_response_status,
)


def test_reset_password_post(
    test_client, session: sqlalchemy.orm.scoping.scoped_session, mocker
):
    """
    Test that POST call to /reset-password endpoint successfully resets the user's password, and verifies the new password digest is distinct from the old one in the database
    """

    user_info = create_test_user_api(test_client)
    old_password_digest = get_user_password_digest(session, user_info)

    token = request_reset_password_api(test_client, mocker, user_info)
    new_password = str(uuid.uuid4())
    response = test_client.post(
        "/api/reset-password",
        json={"email": user_info.email, "token": token, "password": new_password},
    )
    check_response_status(response, HTTPStatus.OK.value)
    new_password_digest = get_user_password_digest(session, user_info)
    assert (
        new_password_digest != old_password_digest
    ), "Old and new password digests should be distinct"
