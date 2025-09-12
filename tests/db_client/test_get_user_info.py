import uuid

import pytest

from middleware.exceptions import UserNotFoundError
from tests.helpers.common_test_data import get_test_name


def test_get_user_info(live_database_client):
    # Add a new user to the database
    email = get_test_name()
    password_digest = uuid.uuid4().hex

    live_database_client.create_new_user(
        email=email,
        password_digest=password_digest,
    )

    # Fetch the user using its email with the DatabaseClient method
    user_info = live_database_client.get_user_info(user_email=email)
    # Confirm the user is retrieved successfully
    assert user_info.password_digest == password_digest
    # Attempt to fetch non-existant user
    # Assert UserNotFoundError is raised
    with pytest.raises(UserNotFoundError):
        live_database_client.get_user_info(user_email="invalid_email")
