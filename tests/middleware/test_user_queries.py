from http import HTTPStatus
from unittest.mock import MagicMock

import pytest

from database_client.database_client import DatabaseClient
from middleware.exceptions import UserNotFoundError, DuplicateUserError
from middleware.primary_resource_logic.login_queries import try_logging_in
from middleware.primary_resource_logic.user_queries import (
    user_post_results,
    user_check_email,
)
from tests.helper_scripts.DynamicMagicMock import DynamicMagicMock
from tests.helper_scripts.common_mocks_and_patches import multi_monkeypatch

PATCH_ROOT = "middleware.primary_resource_logic.user_queries"


@pytest.fixture
def test_user_post_query_mocks(monkeypatch) -> MagicMock:
    mock = MagicMock()
    multi_monkeypatch(
        monkeypatch,
        patch_root=PATCH_ROOT,
        mock=mock,
        functions_to_patch=[
            "generate_password_hash",
            "message_response",
        ],
    )
    return mock


def test_user_post_query(test_user_post_query_mocks):
    mock = test_user_post_query_mocks
    mock.generate_password_hash.return_value = mock.password_digest
    user_post_results(mock.db_client, mock.dto)
    mock.generate_password_hash.assert_called_once_with(mock.dto.password)
    mock.db_client.create_new_user.assert_called_once_with(
        mock.dto.email, mock.password_digest
    )
    mock.message_response.assert_called_once_with(
        status_code=HTTPStatus.OK, message="Successfully added user."
    )


@pytest.mark.parametrize(
    "user_id, expected_exception",
    [
        ("some_user_id", None),  # No exception expected, valid user_id
        (None, UserNotFoundError),  # Exception expected, user_id is None
    ],
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


class TryLoggingInMocks(DynamicMagicMock):
    check_password_hash: MagicMock
    unauthorized_response: MagicMock
    login_response: MagicMock


def setup_try_logging_in_mocks(check_password_hash_return_value):
    # Create Mock values
    mock = TryLoggingInMocks(
        patch_root="middleware.primary_resource_logic.login_queries",
    )
    mock.user_info = DatabaseClient.UserInfo(
        password_digest=mock.password_digest,
        id=mock.user_id,
        api_key=None,
        email=mock.email,
    )
    mock.db_client.get_user_info = MagicMock(return_value=mock.user_info)
    mock.check_password_hash.return_value = check_password_hash_return_value

    return mock


def assert_try_logging_in_preconditions(mock):
    mock.db_client.get_user_info.assert_called_with(mock.dto.email)
    mock.check_password_hash.assert_called_with(
        pwhash=mock.password_digest, password=mock.dto.password
    )


def test_try_logging_in_successful():
    mock = setup_try_logging_in_mocks(check_password_hash_return_value=True)

    # Call function
    try_logging_in(mock.db_client, mock.dto)

    # Assert
    assert_try_logging_in_preconditions(mock)
    mock.unauthorized_response.assert_not_called()
    mock.login_response.assert_called_with(mock.user_info)


def test_try_logging_in_unsuccessful():
    mock = setup_try_logging_in_mocks(check_password_hash_return_value=False)

    # Call function
    try_logging_in(mock.db_client, mock.dto)

    # Assert
    assert_try_logging_in_preconditions(mock)
    mock.unauthorized_response.assert_called_once()
    mock.login_response.assert_not_called()


def test_user_post_results_duplicate_user_error(test_user_post_query_mocks):
    mock = test_user_post_query_mocks
    mock.db_client.create_new_user.side_effect = DuplicateUserError
    user_post_results(mock.db_client, mock.dto)
    mock.db_client.create_new_user.assert_called_once_with(
        mock.dto.email, mock.generate_password_hash.return_value
    )
    mock.message_response.assert_called_once_with(
        message=f"User with email {mock.dto.email} already exists.",
        status_code=HTTPStatus.CONFLICT,
    )
