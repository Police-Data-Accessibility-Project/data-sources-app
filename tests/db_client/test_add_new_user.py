import pytest
from sqlalchemy import select

from db.client.core import DatabaseClient
from db.models.implementations.core.user.core import User
from middleware.exceptions import DuplicateUserError
from tests.helpers.common_test_data import get_test_name


def test_add_new_user(live_database_client: DatabaseClient):
    fake_email = get_test_name()
    live_database_client.create_new_user(fake_email, "test_password")
    result = (
        live_database_client.execute_sqlalchemy(
            lambda: select(User.password_digest, User.api_key).where(
                User.email == fake_email
            )
        )
        .mappings()
        .one_or_none()
    )

    password_digest = result.password_digest

    assert password_digest == "test_password"

    # Adding same user should produce a DuplicateUserError
    with pytest.raises(DuplicateUserError):
        live_database_client.create_new_user(fake_email, "test_password")
