import uuid

from sqlalchemy import update

from db.client.core import DatabaseClient
from db.models.implementations.core.user.core import User
from tests.helpers.common_test_data import get_test_name


def test_get_user_by_api_key(live_database_client: DatabaseClient):
    # Add a new user to the database
    test_email = get_test_name()
    test_api_key = uuid.uuid4().hex

    user_id = live_database_client.create_new_user(
        email=test_email,
        password_digest="test_password",
    )

    # Add a role and api_key to the user
    live_database_client.execute_sqlalchemy(
        lambda: update(User)
        .where(User.email == test_email)
        .values(role="test_role", api_key=test_api_key)
    )

    # Fetch the user's role using its api key with the DatabaseClient method
    user_identifiers = live_database_client.get_user_by_api_key(api_key=test_api_key)

    # Confirm the user_id is retrieved successfully
    assert user_identifiers.id == user_id
