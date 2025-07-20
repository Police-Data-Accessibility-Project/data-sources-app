import uuid

from db.client.core import DatabaseClient
from tests.helpers.common_test_data import get_test_name


def test_update_user_api_key(live_database_client: DatabaseClient):
    # Add a new user to the database
    email = get_test_name()
    password_digest = uuid.uuid4().hex

    live_database_client.create_new_user(
        email=email,
        password_digest=password_digest,
    )

    original_user_info = live_database_client.get_user_info(email)

    # Update the user's API key with the DatabaseClient Method
    live_database_client.update_user_api_key(
        api_key="test_api_key", user_id=original_user_info.id
    )

    # Fetch the user's API key from the database to confirm the change
    user_info = live_database_client.get_user_info(email)
    assert original_user_info.api_key != user_info.api_key
    assert user_info.api_key == "test_api_key"
