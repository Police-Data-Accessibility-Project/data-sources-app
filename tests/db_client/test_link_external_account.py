import uuid

from sqlalchemy import select

from db.client.core import DatabaseClient
from db.enums import ExternalAccountTypeEnum
from db.models.implementations.core.external_account import ExternalAccount
from tests.helper_scripts.common_test_data import get_test_name


def test_link_external_account(live_database_client: DatabaseClient):
    fake_email = get_test_name()
    fake_external_account_id = uuid.uuid4().hex
    live_database_client.create_new_user(fake_email, "test_password")
    user_id = live_database_client.get_user_id(fake_email)
    live_database_client.link_external_account(
        user_id=str(user_id),
        external_account_id=fake_external_account_id,
        external_account_type=ExternalAccountTypeEnum.GITHUB,
    )
    row = (
        live_database_client.execute_sqlalchemy(
            lambda: select(ExternalAccount.user_id, ExternalAccount.account_type).where(
                ExternalAccount.account_identifier == fake_external_account_id
            )
        )
        .mappings()
        .one_or_none()
    )

    assert row.user_id == user_id
    assert row.account_type == ExternalAccountTypeEnum.GITHUB.value
