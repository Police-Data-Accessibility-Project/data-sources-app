import uuid

from db.client.core import DatabaseClient
from tests.helper_scripts.common_test_data import get_test_name


def test_reset_token_logic(live_database_client: DatabaseClient):
    fake_email = get_test_name()
    fake_token = uuid.uuid4().hex
    user_id = live_database_client.create_new_user(fake_email, "test_password")
    live_database_client.add_reset_token(user_id, fake_token)
    reset_token_info = live_database_client.get_reset_token_info(fake_token)
    assert reset_token_info, "Token not found"
    assert reset_token_info.user_id == user_id, "User id does not match"

    live_database_client.delete_reset_token(user_id, fake_token)
    reset_token_info = live_database_client.get_reset_token_info(fake_token)
    assert reset_token_info is None, "Token not deleted"
