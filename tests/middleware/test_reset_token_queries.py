import uuid
from datetime import datetime, timedelta
from http import HTTPStatus
from unittest.mock import MagicMock

import psycopg2.extensions
import pytest

from middleware.custom_exceptions import TokenNotFoundError
from middleware.reset_token_queries import (
    check_reset_token,
    add_reset_token,
    delete_reset_token,
    request_reset_password,
    reset_password,
    set_user_password,
    token_is_expired,
    reset_token_validation,
    validate_token,
    InvalidTokenError,
)
from tests.helper_functions import (
    create_reset_token,
    create_test_user,
    get_reset_tokens_for_email,
    DynamicMagicMock,
)
from tests.fixtures import db_cursor, dev_db_connection


def test_check_reset_token(db_cursor: psycopg2.extensions.cursor) -> None:
    """
    Checks if a token existing in the database
    is properly returned by check_reset_token
    :param db_cursor:
    :return:
    """
    test_token_insert = create_reset_token(db_cursor)

    user_data = check_reset_token(db_cursor, test_token_insert.token)
    assert test_token_insert.id == user_data["id"]


def test_check_reset_token_raises_token_not_found_error(
    db_cursor: psycopg2.extensions,
) -> None:
    with pytest.raises(TokenNotFoundError):
        check_reset_token(db_cursor, token=str(uuid.uuid4()))


def test_add_reset_token(db_cursor: psycopg2.extensions.cursor) -> None:
    """
    Checks if add_reset_token properly inserts a token
    for the given email in the database
    """
    user = create_test_user(db_cursor)
    token = uuid.uuid4().hex
    add_reset_token(db_cursor, user.email, token)
    db_cursor.execute(
        """
        SELECT id, token FROM RESET_TOKENS where email = %s
        """,
        (user.email,),
    )
    results = db_cursor.fetchall()
    assert len(results) == 1
    assert results[0][1] == token


def test_delete_reset_token(db_cursor: psycopg2.extensions.cursor) -> None:
    """
    Checks if token previously inserted is deleted
    by the delete_reset_token method
    """
    reset_token_insert = create_reset_token(db_cursor)
    results = get_reset_tokens_for_email(db_cursor, reset_token_insert)
    assert len(results) == 1
    delete_reset_token(db_cursor, reset_token_insert.email, reset_token_insert.token)
    results = get_reset_tokens_for_email(db_cursor, reset_token_insert)
    assert len(results) == 0


class RequestResetPasswordMocks(DynamicMagicMock):
    cursor: MagicMock
    email: MagicMock
    user_check_email: MagicMock
    generate_api_key: MagicMock
    token: MagicMock
    add_reset_token: MagicMock
    send_password_reset_link: MagicMock
    make_response: MagicMock


def test_request_reset_password(monkeypatch):
    mock = RequestResetPasswordMocks()
    mock.generate_api_key.return_value = mock.token

    monkeypatch.setattr(
        "middleware.reset_token_queries.user_check_email", mock.user_check_email
    )
    monkeypatch.setattr(
        "middleware.reset_token_queries.generate_api_key", mock.generate_api_key
    )
    monkeypatch.setattr(
        "middleware.reset_token_queries.add_reset_token", mock.add_reset_token
    )
    monkeypatch.setattr(
        "middleware.reset_token_queries.send_password_reset_link",
        mock.send_password_reset_link,
    )
    monkeypatch.setattr(
        "middleware.reset_token_queries.make_response", mock.make_response
    )

    request_reset_password(mock.cursor, mock.email)

    mock.user_check_email.assert_called_once_with(mock.cursor, mock.email)
    mock.generate_api_key.assert_called_once()
    mock.add_reset_token.assert_called_once_with(mock.cursor, mock.email, mock.token)
    mock.send_password_reset_link.assert_called_once_with(mock.email, mock.token)
    mock.make_response.assert_called_once_with(
        {
            "message": "An email has been sent to your email address with a link to reset your password. It will be valid for 15 minutes.",
            "token": mock.token,
        },
        HTTPStatus.OK,
    )


class ResetPasswordMocks(DynamicMagicMock):
    cursor: MagicMock
    email: MagicMock
    token: MagicMock
    create_date: MagicMock
    check_reset_token: MagicMock
    token_is_expired: MagicMock
    make_response: MagicMock
    delete_reset_token: MagicMock
    set_user_password: MagicMock
    invalid_token_response: MagicMock


def set_reset_password_monkeypatches(
    monkeypatch: pytest.MonkeyPatch, mock: ResetPasswordMocks
) -> None:
    monkeypatch.setattr(
        "middleware.reset_token_queries.check_reset_token", mock.check_reset_token
    )
    monkeypatch.setattr(
        "middleware.reset_token_queries.token_is_expired", mock.token_is_expired
    )
    monkeypatch.setattr(
        "middleware.reset_token_queries.make_response", mock.make_response
    )
    monkeypatch.setattr(
        "middleware.reset_token_queries.delete_reset_token", mock.delete_reset_token
    )
    monkeypatch.setattr(
        "middleware.reset_token_queries.set_user_password",
        mock.set_user_password,
    )
    monkeypatch.setattr(
        "middleware.reset_token_queries.invalid_token_response",
        mock.invalid_token_response,
    )


def test_reset_password_happy_path(monkeypatch):
    mock = ResetPasswordMocks()
    set_reset_password_monkeypatches(monkeypatch, mock)
    mock.check_reset_token.return_value = {
        "email": mock.email,
        "create_date": mock.create_date,
    }
    mock.token_is_expired.return_value = False

    reset_password(mock.cursor, mock.token, mock.password)

    mock.check_reset_token.assert_called_once_with(mock.cursor, mock.token)
    mock.token_is_expired.assert_called_once_with(token_create_date=mock.create_date)
    mock.invalid_token_response.assert_not_called()
    mock.make_response.assert_called_once_with(
        {"message": "Successfully updated password"}, HTTPStatus.OK
    )
    mock.delete_reset_token.assert_not_called()
    mock.set_user_password.assert_called_once_with(
        mock.cursor, mock.email, mock.password
    )


def test_reset_password_token_not_found(monkeypatch):
    mock = ResetPasswordMocks()
    set_reset_password_monkeypatches(monkeypatch, mock)
    mock.check_reset_token.side_effect = TokenNotFoundError

    reset_password(mock.cursor, mock.token, mock.password)

    mock.check_reset_token.assert_called_once_with(mock.cursor, mock.token)
    mock.token_is_expired.assert_not_called()
    mock.invalid_token_response.assert_called_once()
    mock.make_response.assert_not_called()
    mock.delete_reset_token.assert_not_called()
    mock.set_user_password.assert_not_called()


def test_reset_password_token_is_expired(monkeypatch):
    mock = ResetPasswordMocks()
    set_reset_password_monkeypatches(monkeypatch, mock)
    mock.check_reset_token.return_value = {
        "email": mock.email,
        "create_date": mock.create_date,
    }
    mock.token_is_expired.return_value = True

    reset_password(mock.cursor, mock.token, mock.password)

    mock.check_reset_token.assert_called_once_with(mock.cursor, mock.token)
    mock.token_is_expired.assert_called_once_with(token_create_date=mock.create_date)
    mock.delete_reset_token.assert_called_once_with(mock.cursor, mock.email, mock.token)
    mock.invalid_token_response.assert_called_once()
    mock.make_response.assert_not_called()
    mock.set_user_password.assert_not_called()


def test_set_new_user_password_happy_path(monkeypatch):
    mock_cursor = MagicMock()
    mock_email = MagicMock()
    mock_password = MagicMock()
    mock_password_digest = MagicMock()
    mock_generate_password_hash = MagicMock(return_value=mock_password_digest)
    mock_set_user_password_digest = MagicMock()

    monkeypatch.setattr(
        "middleware.reset_token_queries.set_user_password_digest",
        mock_set_user_password_digest,
    )
    monkeypatch.setattr(
        "middleware.reset_token_queries.generate_password_hash",
        mock_generate_password_hash,
    )

    set_user_password(mock_cursor, mock_email, mock_password)

    mock_generate_password_hash.assert_called_once_with(mock_password)
    mock_set_user_password_digest.assert_called_once_with(
        mock_cursor, mock_email, mock_password_digest
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

def monkeypatch_reset_token_validation(monkeypatch: pytest.MonkeyPatch, mock: ResetTokenValidationMocks) -> None:
    monkeypatch.setattr(
        "middleware.reset_token_queries.make_response", mock.make_response
    )
    monkeypatch.setattr(
        "middleware.reset_token_queries.validate_token",
        mock.validate_token,
    )
    monkeypatch.setattr(
        "middleware.reset_token_queries.invalid_token_response",
        mock.invalid_token_response,
    )

def test_reset_token_validation_happy_path(monkeypatch):
    mocks = ResetTokenValidationMocks()
    monkeypatch_reset_token_validation(monkeypatch, mocks)
    mocks.validate_token.return_value = mocks.email
    reset_token_validation(mocks.cursor, mocks.token)

    mocks.validate_token.assert_called_once_with(mocks.cursor, mocks.token)
    mocks.make_response.assert_called_once_with(
        {"message": "Token is valid"}, HTTPStatus.OK
    )

def test_reset_token_validation_invalid_token(monkeypatch):
    mocks = ResetTokenValidationMocks()
    monkeypatch_reset_token_validation(monkeypatch, mocks)
    mocks.validate_token.side_effect = InvalidTokenError
    reset_token_validation(mocks.cursor, mocks.token)
    mocks.validate_token.assert_called_once_with(mocks.cursor, mocks.token)
    mocks.make_response.assert_not_called()
    mocks.invalid_token_response.assert_called_once()


def test_validate_token_happy_path(monkeypatch):
    mock = ResetPasswordMocks()
    set_reset_password_monkeypatches(monkeypatch, mock)
    mock.check_reset_token.return_value = {
        "email": mock.email,
        "create_date": mock.create_date,
    }
    mock.token_is_expired.return_value = False
    result = validate_token(mock.cursor, mock.token)
    assert result == mock.email
    mock.check_reset_token.assert_called_once_with(mock.cursor, mock.token)
    mock.token_is_expired.assert_called_once_with(token_create_date=mock.create_date)
    mock.delete_reset_token.assert_not_called()


def test_validate_token_token_not_found(monkeypatch):
    mock = ResetPasswordMocks()
    set_reset_password_monkeypatches(monkeypatch, mock)
    mock.check_reset_token.side_effect = TokenNotFoundError
    with pytest.raises(InvalidTokenError):
        result = validate_token(mock.cursor, mock.token)
    mock.check_reset_token.assert_called_once_with(mock.cursor, mock.token)
    mock.token_is_expired.assert_not_called()
    mock.delete_reset_token.assert_not_called()

def test_validate_token_token_is_expired(monkeypatch):
    mock = ResetPasswordMocks()
    set_reset_password_monkeypatches(monkeypatch, mock)
    mock.check_reset_token.return_value = {
        "email": mock.email,
        "create_date": mock.create_date,
    }
    mock.token_is_expired.return_value = True
    with pytest.raises(InvalidTokenError):
        result = validate_token(mock.cursor, mock.token)
    mock.check_reset_token.assert_called_once_with(mock.cursor, mock.token)
    mock.token_is_expired.assert_called_once_with(token_create_date=mock.create_date)
    mock.delete_reset_token.assert_called_once_with(mock.cursor, mock.email, mock.token)
