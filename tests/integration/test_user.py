"""Integration tests for /user endpoint."""

from http import HTTPStatus
import uuid

import psycopg2
import sqlalchemy
from sqlalchemy import select

from conftest import test_client, session
from middleware.models import User
from tests.fixtures import dev_db_connection, client_with_db
from tests.helper_scripts.helper_functions import (
    create_test_user_api,
    get_user_password_digest,
    create_api_key,
    create_test_user_setup,
)


def test_user_post(test_client, session: sqlalchemy.orm.scoping.scoped_session):
    """
    Test that POST call to /user endpoint successfully creates a new user and verifies the user's email and password digest in the database
    """

    user_info = create_test_user_api(test_client)
    row = (
        session.execute(
            select(User.email, User.password_digest).where(
                User.email == user_info.email
            )
        )
        .mappings()
        .one()
    )

    assert user_info.email == row.email, "DB user email and original email do not match"
    assert (
        user_info.password != row.password_digest
    ), "DB user password digest should not match password"


def test_user_put(test_client, session: sqlalchemy.orm.scoping.scoped_session):
    """
    Test that PUT call to /user endpoint successfully updates the user's password and verifies the new password hash is distinct from both the plain new password and the old password hash in the database
    """
    tus = create_test_user_setup(test_client)

    old_password_hash = get_user_password_digest(session, tus.user_info)

    new_password = str(uuid.uuid4())

    response = test_client.put(
        "/api/user",
        headers=tus.authorization_header,
        json={"email": tus.user_info.email, "password": new_password},
    )
    assert (
        response.status_code == HTTPStatus.OK.value
    ), "User password update not successful"

    new_password_hash = get_user_password_digest(session, tus.user_info)

    assert (
        new_password != new_password_hash
    ), "Password and password hash should be distinct after password update"
    assert (
        new_password_hash != old_password_hash
    ), "Password hashes should be different on update"
