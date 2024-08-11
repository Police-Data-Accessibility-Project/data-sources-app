import datetime
import uuid
from http import HTTPStatus
from typing import Callable

import flask
import pytest
from unittest.mock import MagicMock, patch

from flask import Flask

from middleware import security
from middleware.security import (
    get_api_key_from_header,
    get_authorization_header,
    extract_api_key_from_header,
    check_for_properly_formatted_authorization_header,
    check_for_header_with_authorization_key,
    check_user_permission,
    get_user_id_from_database,
    check_api_key,
)
from middleware.decorators import api_key_required
from tests.helper_scripts.DymamicMagicMock import DynamicMagicMock

PATCH_ROOT = "middleware.security"


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
    @api_key_required
    def _dummy_route():
        return "This is a protected route", HTTPStatus.OK.value

    return _dummy_route


DUMMY_AUTHORIZATION = {"Authorization": "Basic valid_api_key"}


class ValidateHeaderMocks(DynamicMagicMock):
    check_for_header_with_authorization_key: MagicMock
    extract_api_key_from_header: MagicMock
    api_key: MagicMock


def test_validate_header():
    mock = ValidateHeaderMocks(
        patch_root=PATCH_ROOT,
        mocks_to_patch=[
            "check_for_header_with_authorization_key",
            "extract_api_key_from_header",
        ],
    )
    mock.extract_api_key_from_header.return_value = mock.api_key
    api_key = get_api_key_from_header()
    mock.check_for_header_with_authorization_key.assert_called_once()
    mock.extract_api_key_from_header.assert_called_once()
    assert api_key == mock.api_key


def test_get_authorization_header():
    # Mock the request headers
    request = MagicMock()
    request.headers = {"Authorization": "Bearer token123"}

    # Patch the request object to return our mocked request
    with patch(f"{PATCH_ROOT}.request", request):
        # Test with a valid authorization header
        authorization_header = get_authorization_header()
        assert authorization_header == ["Bearer", "token123"]

        # Test with a different authorization header format
        request.headers = {"Authorization": "Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ=="}
        authorization_header = get_authorization_header()
        assert authorization_header == ["Basic", "QWxhZGRpbjpvcGVuIHNlc2FtZQ=="]


class ExtractApiKeyFromHeaderMocks(DynamicMagicMock):
    get_authorization_header: MagicMock
    check_for_properly_formatted_authorization_header: MagicMock


def test_extract_api_key_from_header():
    mock = ExtractApiKeyFromHeaderMocks(
        patch_root=PATCH_ROOT,
        mocks_to_patch=[
            "get_authorization_header",
            "check_for_properly_formatted_authorization_header",
        ],
        return_values={
            "get_authorization_header": ["Basic", "QWxhZGRpbjpvcGVuIHNlc2FtZQ=="],
        },
    )

    api_key = extract_api_key_from_header()
    mock.get_authorization_header.assert_called_once()
    mock.check_for_properly_formatted_authorization_header.assert_called_once()
    assert api_key == "QWxhZGRpbjpvcGVuIHNlc2FtZQ=="


@pytest.fixture
def mock_abort(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr(f"{PATCH_ROOT}.abort", mock)
    return mock


def test_check_for_properly_formatted_authorization_header_success(mock_abort):
    authorization_header = ["Basic", "QWxhZGRpbjpvcGVuIHNlc2FtZQ=="]
    check_for_properly_formatted_authorization_header(authorization_header)
    mock_abort.assert_not_called()


def test_check_for_properly_formatted_authorization_header_failure_not_basic(
    mock_abort,
):
    authorization_header = ["Bearer", "QWxhZGRpbjpvcGVuIHNlc2FtZQ=="]
    check_for_properly_formatted_authorization_header(authorization_header)
    mock_abort.assert_called_once_with(
        code=HTTPStatus.BAD_REQUEST,
        message="Please provide a properly formatted Basic token and API key",
    )


def test_check_for_properly_formatted_authorization_header_failure_not_properly_formatted(
    mock_abort,
):
    authorization_header = ["Basic"]
    check_for_properly_formatted_authorization_header(authorization_header)
    mock_abort.assert_called_once_with(
        code=HTTPStatus.BAD_REQUEST,
        message="Please provide a properly formatted Basic token and API key",
    )


@pytest.fixture
def mock_request(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr(f"{PATCH_ROOT}.request", mock)
    return mock


def test_check_for_header_with_authorization_key_success(mock_abort, mock_request):
    mock_request.headers = DUMMY_AUTHORIZATION
    check_for_header_with_authorization_key()
    mock_abort.assert_not_called()


def test_check_for_header_with_authorization_key_failure_no_request_header(
    mock_abort, mock_request
):
    mock_request.headers = None
    check_for_header_with_authorization_key()
    mock_abort.assert_called_once_with(
        code=HTTPStatus.BAD_REQUEST,
        message="Please provide an 'Authorization' key in the request header",
    )


def test_check_for_header_with_authorization_key_failure_no_authorization_header(
    mock_abort, mock_request
):
    mock_request.headers = {"Dummy": "Dummy"}
    check_for_header_with_authorization_key()
    mock_abort.assert_called_once_with(
        code=HTTPStatus.BAD_REQUEST,
        message="Please provide an 'Authorization' key in the request header",
    )


class CheckUserPermissionMocks(DynamicMagicMock):
    db_client: MagicMock
    user_id: MagicMock
    permission: MagicMock
    abort: MagicMock


def test_check_user_permission_permission_is_none(mock_abort):
    mock = CheckUserPermissionMocks()
    check_user_permission(mock.db_client, mock.user_id, None)
    mock.db_client.get_user_permissions.assert_not_called()
    mock_abort.assert_not_called()


def test_check_user_permission_permission_in_user_permissions(mock_abort):
    mock = CheckUserPermissionMocks()
    mock.db_client.get_user_permissions.return_value = [mock.permission]
    check_user_permission(mock.db_client, mock.user_id, mock.permission)
    mock.db_client.get_user_permissions.assert_called_once_with(mock.user_id)
    mock_abort.assert_not_called()


def test_check_user_permission_permission_not_in_user_permissions(mock_abort):
    mock = CheckUserPermissionMocks()
    mock.db_client.get_user_permissions.return_value = []
    check_user_permission(mock.db_client, mock.user_id, mock.permission)
    mock.db_client.get_user_permissions.assert_called_once_with(mock.user_id)
    mock_abort.assert_called_once_with(
        HTTPStatus.FORBIDDEN, "You do not have permission to access this endpoint"
    )


class GetUserIdFromDatabaseMocks(DynamicMagicMock):
    db_client: MagicMock
    user_id: MagicMock
    api_key: MagicMock


def test_get_user_id_from_database_happy_path(mock_abort):
    mock = GetUserIdFromDatabaseMocks()
    mock.db_client.get_user_by_api_key.return_value = mock.user_id
    user_id = get_user_id_from_database(mock.db_client, mock.api_key)
    mock.db_client.get_user_by_api_key.assert_called_once_with(mock.api_key)
    mock_abort.assert_not_called()
    assert user_id == mock.user_id


def test_get_user_id_from_database_invalid_api_key(mock_abort):
    mock = GetUserIdFromDatabaseMocks()
    mock.db_client.get_user_by_api_key.return_value = None
    user_id = get_user_id_from_database(mock.db_client, mock.api_key)
    mock.db_client.get_user_by_api_key.assert_called_once_with(mock.api_key)
    mock_abort.assert_called_once_with(HTTPStatus.UNAUTHORIZED, "Invalid API Key")
    assert user_id is None


class CheckApiKeyMocks(DynamicMagicMock):
    permission: MagicMock
    db_client: MagicMock
    get_db_client: MagicMock
    get_api_key_from_header: MagicMock
    get_user_id_from_database: MagicMock
    check_user_permission: MagicMock
    user_id: MagicMock
    api_key: MagicMock


def test_check_api_key():
    mock = CheckApiKeyMocks(
        patch_root=PATCH_ROOT,
        mocks_to_patch=[
            "get_user_id_from_database",
            "check_user_permission",
            "get_db_client",
            "get_api_key_from_header",
        ],
    )
    mock.get_api_key_from_header.return_value = mock.api_key
    mock.get_user_id_from_database.return_value = mock.user_id
    mock.get_db_client.return_value = mock.db_client

    check_api_key(mock.permission)

    mock.get_api_key_from_header.assert_called_once()
    mock.get_db_client.assert_called_once()
    mock.get_user_id_from_database.assert_called_once_with(mock.db_client, mock.api_key)
    mock.check_user_permission.assert_called_once_with(mock.db_client, mock.user_id, mock.permission)

