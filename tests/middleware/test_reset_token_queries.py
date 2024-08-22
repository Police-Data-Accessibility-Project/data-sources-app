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
from tests.helper_scripts.DynamicMagicMock import DynamicMagicMock


class RequestResetPasswordMocks(DynamicMagicMock):
    user_check_email: MagicMock
    generate_api_key: MagicMock
    send_password_reset_link: MagicMock
    make_response: MagicMock


def test_request_reset_password(monkeypatch):
    mock = RequestResetPasswordMocks(
        patch_root="middleware.reset_token_queries",
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
    make_response: MagicMock
    set_user_password: MagicMock
    invalid_token_response: MagicMock
    validate_token: MagicMock


@pytest.fixture
def setup_reset_password_mocks():
    mock = ResetPasswordMocks(
        patch_root="middleware.reset_token_queries",
        return_values={"invalid_token_response": MagicMock()},
    )
    mock.validate_token.return_value = mock.email
    yield mock


def test_reset_password_happy_path(setup_reset_password_mocks):
    mock = setup_reset_password_mocks

    reset_password(mock.db_client, mock.dto)

    mock.invalid_token_response.assert_not_called()
    mock.make_response.assert_called_once_with(
        {"message": "Successfully updated password"}, HTTPStatus.OK
    )
    mock.set_user_password.assert_called_once_with(
        mock.db_client, mock.email, mock.dto.token
    )


def test_reset_password_invalid_token(setup_reset_password_mocks):
    mock = setup_reset_password_mocks

    mock.validate_token.side_effect = InvalidTokenError

    mock_response = reset_password(mock.cursor, mock.dto)

    assert mock_response == mock.invalid_token_response.return_value
    mock.invalid_token_response.assert_called_once()
    mock.make_response.assert_not_called()
    mock.set_user_password.assert_not_called()


class ValidateTokenMocks(DynamicMagicMock):
    token_is_expired: MagicMock


@pytest.fixture
def setup_validate_token_mocks(monkeypatch) -> ValidateTokenMocks:
    mock = ValidateTokenMocks(
        patch_root="middleware.reset_token_queries",
    )
    mock.token_data.email = mock.email
    return mock


def assert_validate_token_precondition_calls(mock: ValidateTokenMocks):
    mock.db_client.get_reset_token_info.assert_called_once_with(mock.token)


def test_validate_token_happy_path(monkeypatch, setup_validate_token_mocks):
    mock = setup_validate_token_mocks

    mock.db_client.get_reset_token_info.return_value = mock.token_data
    mock.token_is_expired.return_value = False

    email = validate_token(mock.db_client, mock.token)

    assert email == mock.email

    assert_validate_token_precondition_calls(mock)

    mock.token_is_expired.assert_called_once_with(
        token_create_date=mock.token_data.create_date
    )
    mock.db_client.delete_reset_token.assert_not_called()


def test_validate_token_token_not_found(monkeypatch, setup_validate_token_mocks):
    mock = setup_validate_token_mocks

    mock.db_client.get_reset_token_info.return_value = None

    with pytest.raises(InvalidTokenError):
        email = validate_token(mock.db_client, mock.token)

    assert_validate_token_precondition_calls(mock)

    mock.token_is_expired.assert_not_called()
    mock.db_client.delete_reset_token.assert_not_called()


def test_validate_token_token_is_expired(monkeypatch, setup_validate_token_mocks):
    mock = setup_validate_token_mocks

    mock.db_client.get_reset_token_info.return_value = mock.token_data
    mock.token_is_expired.return_value = True

    with pytest.raises(InvalidTokenError):
        email = validate_token(mock.db_client, mock.token)

    assert_validate_token_precondition_calls(mock)

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


@pytest.mark.parametrize(
    "token_age_seconds, expected_result",
    [
        (1000, True),  # Token is expired
        (800, False),  # Token is not expired
    ],
)
def test_token_is_expired(token_age_seconds, expected_result):
    token_create_date = datetime.utcnow() - timedelta(seconds=token_age_seconds)
    expired = token_is_expired(token_create_date)
    assert expired == expected_result


class ResetTokenValidationMocks(DynamicMagicMock):
    validate_token: MagicMock
    make_response: MagicMock
    invalid_token_response: MagicMock


@pytest.fixture
def setup_reset_token_validation_mocks():
    mock = ResetTokenValidationMocks(
        patch_root="middleware.reset_token_queries",
    )
    mock.validate_token.return_value = mock.email
    return mock


def assert_reset_token_validation_precondition_calls(mock: ResetTokenValidationMocks):
    mock.validate_token.assert_called_once_with(mock.cursor, mock.token)


def test_reset_token_validation_happy_path(setup_reset_token_validation_mocks):
    mocks = setup_reset_token_validation_mocks

    reset_token_validation(mocks.cursor, mocks.token)

    assert_reset_token_validation_precondition_calls(mocks)

    mocks.make_response.assert_called_once_with(
        {"message": "Token is valid"}, HTTPStatus.OK
    )


def test_reset_token_validation_invalid_token(setup_reset_token_validation_mocks):
    mocks = setup_reset_token_validation_mocks

    mocks.validate_token.side_effect = InvalidTokenError

    reset_token_validation(mocks.cursor, mocks.token)

    assert_reset_token_validation_precondition_calls(mocks)

    mocks.make_response.assert_not_called()
    mocks.invalid_token_response.assert_called_once()
