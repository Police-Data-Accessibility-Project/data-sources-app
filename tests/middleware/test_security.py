import datetime
import uuid
from http import HTTPStatus
from typing import Callable

import flask
import pytest
from unittest.mock import patch, MagicMock

import requests
from flask import Flask

from middleware import security
from middleware.custom_exceptions import UserNotFoundError
from middleware.login_queries import create_session_token
from middleware.security import (
    validate_api_key,
    APIKeyStatus,
    api_required,
    NoAPIKeyError,
    ExpiredAPIKeyError,
    InvalidAPIKeyError,
    InvalidRoleError,
)
from tests.helper_functions import (
    create_test_user,
    UserInfo,
    give_user_admin_role,
    create_api_key_db,
)
from tests.fixtures import dev_db_connection


def test_api_key_exists_in_users_table_with_admin_role(dev_db_connection):
    cursor = dev_db_connection.cursor()
    test_user = create_test_user(cursor)
    give_user_admin_role(dev_db_connection, UserInfo(test_user.email, ""))
    api_key = create_api_key_db(cursor, test_user.id)
    dev_db_connection.commit()
    result = validate_api_key(api_key, "", "")
    assert result is None


def test_api_key_exists_in_users_table_with_non_admin_role(dev_db_connection):
    cursor = dev_db_connection.cursor()
    test_user = create_test_user(cursor)
    api_key = create_api_key_db(cursor, test_user.id)
    dev_db_connection.commit()
    result = validate_api_key(api_key, "", "")
    assert result is None


def test_api_key_not_in_users_table_but_in_session_tokens_table(dev_db_connection):
    # TODO: REWORK
    cursor = dev_db_connection.cursor()
    test_user = create_test_user(cursor)
    token = create_session_token(cursor, test_user.id, test_user.email)
    dev_db_connection.commit()
    result = validate_api_key(token, "", "")
    assert result is None


def test_expired_session_token(dev_db_connection):
    cursor = dev_db_connection.cursor()
    test_user = create_test_user(cursor)
    token = create_session_token(cursor, test_user.id, test_user.email)
    cursor.execute(
        f"UPDATE session_tokens SET expiration_date = '{datetime.date(year=2020, month=3, day=4)}' WHERE token = '{token}'"
    )
    dev_db_connection.commit()
    with pytest.raises(ExpiredAPIKeyError):
        result = validate_api_key(token, "", "")


def test_session_token_with_admin_role(dev_db_connection):
    # TODO: REWORK
    cursor = dev_db_connection.cursor()
    test_user = create_test_user(cursor)
    give_user_admin_role(dev_db_connection, UserInfo(test_user.email, ""))
    token = create_session_token(cursor, test_user.id, test_user.email)
    dev_db_connection.commit()
    result = validate_api_key(token, "", "")
    assert result is None


def test_api_key_exists_in_access_tokens_table(dev_db_connection):
    cursor = dev_db_connection.cursor()
    token = uuid.uuid4().hex
    expiration = datetime.datetime(year=2030, month=1, day=1)
    cursor.execute(
        f"insert into access_tokens (token, expiration_date) values (%s, %s)",
        (token, expiration),
    )
    dev_db_connection.commit()
    result = validate_api_key(token, "", "")
    assert result is None


def test_api_key_not_exist_in_any_table(dev_db_connection):
    token = uuid.uuid4().hex
    with pytest.raises(InvalidAPIKeyError) as e:
        result = validate_api_key(token, "", "")
    assert "API Key not found" in str(e.value)


def test_expired_access_token_in_access_tokens_table(dev_db_connection):
    cursor = dev_db_connection.cursor()
    token = uuid.uuid4().hex
    expiration = datetime.datetime(year=1999, month=1, day=1)
    cursor.execute(
        f"insert into access_tokens (token, expiration_date) values (%s, %s)",
        (token, expiration),
    )
    dev_db_connection.commit()
    with pytest.raises(InvalidAPIKeyError) as e:
        result = validate_api_key(token, "", "")
    assert "API Key not found" in str(e.value)


def test_admin_only_action_with_non_admin_role(dev_db_connection):
    cursor = dev_db_connection.cursor()
    test_user = create_test_user(cursor)
    api_key = create_api_key_db(cursor, test_user.id)
    dev_db_connection.commit()
    with pytest.raises(InvalidRoleError) as e:
        result = validate_api_key(api_key, "datasources", "PUT")
    assert "You do not have permission to access this endpoint" in str(e.value)


def test_admin_only_action_with_admin_role(dev_db_connection):
    cursor = dev_db_connection.cursor()
    test_user = create_test_user(cursor)
    give_user_admin_role(dev_db_connection, UserInfo(test_user.email, ""))
    api_key = create_api_key_db(cursor, test_user.id)
    dev_db_connection.commit()
    result = validate_api_key(api_key, "datasources", "PUT")
    assert result is None


@pytest.fixture
def app() -> Flask:
    app = Flask(__name__)
    return app


@pytest.fixture
def client(app: Flask):
    return app.test_client()


@pytest.fixture
def mock_request_headers(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr(flask, "request", mock)
    return mock


@pytest.fixture
def mock_validate_api_key(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr(security, "validate_api_key", mock)
    return mock


@pytest.fixture
def dummy_route():
    @api_required
    def _dummy_route():
        return "This is a protected route", HTTPStatus.OK.value

    return _dummy_route


def test_api_required_happy_path(
    app, client, mock_request_headers, mock_validate_api_key, dummy_route: Callable
):
    mock_validate_api_key.return_value = None
    with app.test_request_context(headers={"Authorization": "Bearer valid_api_key"}):
        response = dummy_route()
        assert response == ("This is a protected route", HTTPStatus.OK.value)


def test_api_required_api_key_expired(
    app, client, mock_request_headers, mock_validate_api_key, dummy_route: Callable
):
    mock_validate_api_key.side_effect = ExpiredAPIKeyError(
        "The provided API key has expired"
    )
    with app.test_request_context(headers={"Authorization": "Bearer valid_api_key"}):
        response = dummy_route()
        assert response == (
            {"message": "The provided API key has expired"},
            HTTPStatus.UNAUTHORIZED.value,
        )


def test_api_required_expired_api_key(
    app, client, mock_request_headers, mock_validate_api_key, dummy_route: Callable
):
    mock_validate_api_key.side_effect = ExpiredAPIKeyError(
        "The provided API key has expired"
    )
    with app.test_request_context(headers={"Authorization": "Bearer expired_api_key"}):
        response = dummy_route()
        assert response == (
            {"message": "The provided API key has expired"},
            HTTPStatus.UNAUTHORIZED.value,
        )


def test_api_required_no_api_key_in_request_header(
    app, client, mock_request_headers, mock_validate_api_key, dummy_route: Callable
):
    with app.test_request_context(headers={"Authorization": "Bearer"}):
        response = dummy_route()
        assert response == (
            {"message": "Please provide a properly formatted bearer token and API key"},
            HTTPStatus.BAD_REQUEST.value,
        )


def test_api_required_invalid_role(
    app, client, mock_request_headers, mock_validate_api_key, dummy_route: Callable
):
    mock_validate_api_key.side_effect = InvalidRoleError(
        "You do not have permission to access this endpoint"
    )
    with app.test_request_context(headers={"Authorization": "Bearer valid_api_key"}):
        response = dummy_route()
        assert response == (
            {"message": "You do not have permission to access this endpoint"},
            HTTPStatus.FORBIDDEN.value,
        )


def test_api_required_not_authorization_key_in_request_header(
    app, client, mock_request_headers, mock_validate_api_key, dummy_route: Callable
):
    with app.test_request_context(headers={}):
        response = dummy_route()
        assert response == (
            {"message": "Please provide an 'Authorization' key in the request header"},
            HTTPStatus.BAD_REQUEST.value,
        )


def test_api_required_improperly_formatted_authorization_key(
    app, client, mock_request_headers, mock_validate_api_key, dummy_route: Callable
):
    with app.test_request_context(headers={"Authorization": "Bearer"}):
        response = dummy_route()
        assert response == (
            {"message": "Please provide a properly formatted bearer token and API key"},
            HTTPStatus.BAD_REQUEST.value,
        )


def test_api_required_undefined_api_key(
    app, client, mock_request_headers, mock_validate_api_key, dummy_route: Callable
):
    with app.test_request_context(headers={"Authorization": "Bearer undefined"}):
        response = dummy_route()
        assert response == (
            {"message": "Please provide an API key"},
            HTTPStatus.BAD_REQUEST.value,
        )
