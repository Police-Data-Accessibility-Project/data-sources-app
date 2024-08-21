from unittest.mock import MagicMock

import pytest

from middleware.custom_exceptions import UserNotFoundError
from middleware.user_queries import user_post_results, user_check_email
from tests.helper_scripts.DynamicMagicMock import DynamicMagicMock


def test_user_post_query(monkeypatch):
    mock = MagicMock()
    mock.generate_password_hash.return_value = mock.password_digest

    monkeypatch.setattr(
        "middleware.user_queries.generate_password_hash", mock.generate_password_hash
    )

    user_post_results(mock.db_client, mock.dto)

    mock.generate_password_hash.assert_called_once_with(mock.dto.password)
    mock.db_client.add_new_user.assert_called_once_with(mock.dto.email, mock.password_digest)

@pytest.mark.parametrize(
    "user_id, expected_exception",
    [
        ("some_user_id", None),           # No exception expected, valid user_id
        (None, UserNotFoundError),        # Exception expected, user_id is None
    ]
)
def test_user_check_email(user_id, expected_exception) -> None:
    mock = MagicMock()
    mock.db_client.get_user_id.return_value = user_id

    if expected_exception:
        with pytest.raises(expected_exception):
            user_check_email(mock.db_client, mock.email)
    else:
        user_check_email(mock.db_client, mock.email)

    mock.db_client.get_user_id.assert_called_once_with(mock.email)