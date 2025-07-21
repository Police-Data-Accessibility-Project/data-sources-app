import uuid

from db.client.core import DatabaseClient
from db.enums import ExternalAccountTypeEnum
from tests.helpers.common_test_data import get_test_name


def test_get_user_info_by_external_account_id(live_database_client: DatabaseClient):
    fake_email = get_test_name()
    fake_external_account_id = uuid.uuid4().hex
    live_database_client.create_new_user(fake_email, "test_password")
    user_id = live_database_client.get_user_id(fake_email)
    live_database_client.link_external_account(
        user_id=str(user_id),
        external_account_id=fake_external_account_id,
        external_account_type=ExternalAccountTypeEnum.GITHUB,
    )
    user_info = live_database_client.get_user_info_by_external_account_id(
        fake_external_account_id, ExternalAccountTypeEnum.GITHUB
    )
    assert user_info.email == fake_email
