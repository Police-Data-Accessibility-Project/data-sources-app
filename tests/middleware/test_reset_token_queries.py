from datetime import datetime, timedelta
from http import HTTPStatus
from unittest.mock import MagicMock

import pytest

from middleware.reset_token_queries import (
    request_reset_password,
    reset_password,
    set_user_password,
    token_is_expired,
    reset_token_validation,
    validate_token,
    InvalidTokenError,
)
from tests.helper_scripts.DymamicMagicMock import DynamicMagicMock


class RequestResetPasswordMocks(DynamicMagicMock):
    db_client: MagicMock
    email: MagicMock
    user_check_email: MagicMock
    generate_api_key: MagicMock
    token: MagicMock
    send_password_reset_link: MagicMock
    make_response: MagicMock

def test_request_reset_password(monkeypatch):
    mock = RequestResetPasswordMocks(
        patch_root="middleware.reset_token_queries",
        mocks_to_patch=["user_check_email", "generate_api_key", "send_password_reset_link", "make_response"],
    )
    mock.generate_api_key.return_value = mock.token
    request_reset_password(mock.db_client, mock.email)

    mock.user_check_email.assert_called_once_with(mock.db_client, mock.email)
    mock.generate_api_key.assert_called_once()
    mock.db_client.add_reset_token.assert_called_once_with(mock.email, mock.token)
    mock.send_password_reset_link.assert_called_once_with(mock.email, mock.token)
    mock.make_response.assert_called_once_with(
        {
            "message": "An email has been sent to your email address with a link to reset your password. It will be valid for 15 minutes.",
            "token": mock.token,
        },
        HTTPStatus.OK,
    )


class ResetPasswordMocks(DynamicMagicMock):
    db_client: MagicMock
    email: MagicMock
    token: MagicMock
    make_response: MagicMock
    set_user_password: MagicMock
    invalid_token_response: MagicMock
    validate_token: MagicMock


def test_reset_password_happy_path(monkeypatch):
    mock = ResetPasswordMocks(
        patch_root="middleware.reset_token_queries",
        mocks_to_patch=[
            "validate_token",
            "make_response",
            "set_user_password",
            "delete_reset_token",
            "invalid_token_response",
        ],
    )
    mock.validate_token.return_value = mock.email

    reset_password(mock.db_client, mock.token, mock.password)

    mock.invalid_token_response.assert_not_called()
    mock.make_response.assert_called_once_with(
        {"message": "Successfully updated password"}, HTTPStatus.OK
    )
    mock.delete_reset_token.assert_not_called()
    mock.set_user_password.assert_called_once_with(
        mock.db_client, mock.email, mock.password
    )


def test_reset_password_invalid_token(monkeypatch):
    mock = ResetPasswordMocks(
        patch_root="middleware.reset_token_queries",
        mocks_to_patch=[
            "validate_token",
            "make_response",
            "set_user_password",
            "delete_reset_token",
            "invalid_token_response",
        ],
        return_values={"invalid_token_response": MagicMock()},
    )
    # set_reset_password_monkeypatches(monkeypatch, mock)
    mock.validate_token.side_effect = InvalidTokenError

    mock_response = reset_password(mock.cursor, mock.token, mock.password)

    assert mock_response == mock.invalid_token_response.return_value

    mock.invalid_token_response.assert_called_once()
    mock.make_response.assert_not_called()
    mock.set_user_password.assert_not_called()


class ValidateTokenMocks(DynamicMagicMock):
    db_client: MagicMock
    email: MagicMock
    token: MagicMock
    token_data: MagicMock
    token_is_expired: MagicMock


@pytest.fixture
def setup_validate_token_mocks(monkeypatch) -> ValidateTokenMocks:
    mock = ValidateTokenMocks(
        patch_root="middleware.reset_token_queries",
        mocks_to_patch=["token_is_expired"],
    )
    return mock


def test_validate_token_happy_path(monkeypatch, setup_validate_token_mocks):
    mock = setup_validate_token_mocks
    mock.token_data.email = mock.email
    mock.db_client.get_reset_token_info.return_value = mock.token_data
    mock.token_is_expired.return_value = False

    email = validate_token(mock.db_client, mock.token)

    assert email == mock.email

    mock.db_client.get_reset_token_info.assert_called_once_with(mock.token)
    mock.token_is_expired.assert_called_once_with(
        token_create_date=mock.token_data.create_date
    )
    mock.db_client.delete_reset_token.assert_not_called()


def test_validate_token_token_not_found(monkeypatch, setup_validate_token_mocks):
    mock = setup_validate_token_mocks
    mock.db_client.get_reset_token_info.return_value = None

    with pytest.raises(InvalidTokenError):
        email = validate_token(mock.db_client, mock.token)

    mock.db_client.get_reset_token_info.assert_called_once_with(mock.token)
    mock.token_is_expired.assert_not_called()
    mock.db_client.delete_reset_token.assert_not_called()


def test_validate_token_token_is_expired(monkeypatch, setup_validate_token_mocks):
    mock = setup_validate_token_mocks
    mock.token_data.email = mock.email
    mock.db_client.get_reset_token_info.return_value = mock.token_data
    mock.token_is_expired.return_value = True

    with pytest.raises(InvalidTokenError):
        email = validate_token(mock.db_client, mock.token)

    mock.db_client.get_reset_token_info.assert_called_once_with(mock.token)
    mock.token_is_expired.assert_called_once_with(
        token_create_date=mock.token_data.create_date
    )
    mock.db_client.delete_reset_token.assert_called_once_with(mock.email, mock.token)


def test_set_new_user_password_happy_path(monkeypatch):
    mock_db_client = MagicMock()
    mock_email = MagicMock()
    mock_password = MagicMock()
    mock_password_digest = MagicMock()
    mock_generate_password_hash = MagicMock(return_value=mock_password_digest)

    monkeypatch.setattr(
        "middleware.reset_token_queries.generate_password_hash",
        mock_generate_password_hash,
    )

    set_user_password(mock_db_client, mock_email, mock_password)

    mock_generate_password_hash.assert_called_once_with(mock_password)
    mock_db_client.set_user_password_digest.assert_called_once_with(
        mock_email, mock_password_digest
    )


def test_token_is_expired_true():
    token_create_date = datetime.utcnow() - timedelta(seconds=1000)
    expired = token_is_expired(token_create_date)
    assert expired


def test_token_is_expired_false():
    token_create_date = datetime.utcnow() - timedelta(seconds=800)
    expired = token_is_expired(token_create_date)
    assert not expired


class ResetTokenValidationMocks(DynamicMagicMock):
    cursor: MagicMock
    token: MagicMock
    validate_token: MagicMock
    make_response: MagicMock
    invalid_token_response: MagicMock


def test_reset_token_validation_happy_path(monkeypatch):
    mocks = ResetTokenValidationMocks(
        patch_root="middleware.reset_token_queries",
        mocks_to_patch=["validate_token", "make_response", "invalid_token_response"],
    )
    mocks.validate_token.return_value = mocks.email
    reset_token_validation(mocks.cursor, mocks.token)

    mocks.validate_token.assert_called_once_with(mocks.cursor, mocks.token)
    mocks.make_response.assert_called_once_with(
        {"message": "Token is valid"}, HTTPStatus.OK
    )


def test_reset_token_validation_invalid_token(monkeypatch):
    mocks = ResetTokenValidationMocks(
        patch_root="middleware.reset_token_queries",
        mocks_to_patch=["validate_token", "make_response", "invalid_token_response"],
    )
    mocks.validate_token.side_effect = InvalidTokenError
    reset_token_validation(mocks.cursor, mocks.token)
    mocks.validate_token.assert_called_once_with(mocks.cursor, mocks.token)
    mocks.make_response.assert_not_called()
    mocks.invalid_token_response.assert_called_once()
