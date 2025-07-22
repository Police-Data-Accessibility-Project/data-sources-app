from sqlalchemy import select

from db.client.core import DatabaseClient
from db.models.implementations.core.user.core import User
from tests.helpers.common_test_data import get_test_name


def test_get_user_id(live_database_client: DatabaseClient):
    # Add a new user to the database
    fake_email = get_test_name()
    live_database_client.create_new_user(fake_email, "test_password")

    # Directly fetch the user ID from the database for comparison
    direct_user_id = live_database_client.execute_sqlalchemy(
        lambda: select(User.id).where(User.email == fake_email)
    ).one_or_none()[0]

    # Get the user ID from the live database
    result_user_id = live_database_client.get_user_id(fake_email)

    # Compare the two user IDs
    assert result_user_id == direct_user_id
