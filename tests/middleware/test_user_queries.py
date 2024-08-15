from unittest.mock import MagicMock

import pytest

from middleware.custom_exceptions import UserNotFoundError
from middleware.user_queries import user_post_results, user_check_email
from tests.helper_scripts.DymamicMagicMock import DynamicMagicMock


def test_user_post_query(monkeypatch):

    mock_db_client = MagicMock()
    mock_generate_password_hash = MagicMock()
    mock_generate_password_hash.return_value = "password_digest"

    monkeypatch.setattr(
        "middleware.user_queries.generate_password_hash", mock_generate_password_hash
    )

    user_post_results(mock_db_client, "test_email", "test_password")

    mock_generate_password_hash.assert_called_once_with("test_password")
    mock_db_client.add_new_user.assert_called_once_with("test_email", "password_digest")


class TestUserMagicMock(DynamicMagicMock):
    db_client: MagicMock
    user_id: MagicMock
    email: MagicMock



@pytest.mark.parametrize(
    "user_id, expected_exception",
    [
        ("some_user_id", None),           # No exception expected, valid user_id
        (None, UserNotFoundError),        # Exception expected, user_id is None
    ]
)
def test_user_check_email(user_id, expected_exception) -> None:
    mock = TestUserMagicMock()
    mock.db_client.get_user_id.return_value = user_id

    if expected_exception:
        with pytest.raises(expected_exception):
            user_check_email(mock.db_client, mock.email)
    else:
        user_check_email(mock.db_client, mock.email)

    mock.db_client.get_user_id.assert_called_once_with(mock.email)