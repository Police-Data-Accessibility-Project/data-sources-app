import datetime
import uuid
from http import HTTPStatus
from typing import Callable

import dotenv
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
    check_api_key_associated_with_user,
    check_api_key,
    check_permissions,
)
from middleware.decorators import api_key_required
from tests.helper_scripts.DynamicMagicMock import DynamicMagicMock

PATCH_ROOT = "middleware.security"


@pytest.fixture
def app() -> Flask:
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_ECHO"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = get_env_variable(
        "DEV_DB_CONN_STRING"
    )
    db.init_app(app)
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


class CheckPermissionsMocks(DynamicMagicMock):
    user_email: MagicMock
    db_client: MagicMock
    get_jwt_identity: MagicMock
    verify_jwt_in_request: MagicMock
    get_db_client: MagicMock
    PermissionsManager: MagicMock
    permissions_manager_instance: MagicMock
    permission: MagicMock
    abort: MagicMock


@pytest.fixture
def check_permissions_mocks():
    mock = CheckPermissionsMocks(
        patch_root=PATCH_ROOT,
        mocks_to_patch=[
            "get_jwt_identity",
            "get_db_client",
            "PermissionsManager",
            "abort",
            "verify_jwt_in_request",
        ],
    )
    mock.get_jwt_identity.return_value = mock.user_email
    mock.get_db_client.return_value = mock.db_client
    mock.PermissionsManager.return_value = mock.permissions_manager_instance
    return mock


def assert_pre_conditional_check_permission_mocks(mock: CheckPermissionsMocks):
    mock.verify_jwt_in_request.assert_called_once()
    mock.get_jwt_identity.assert_called_once()
    mock.get_db_client.assert_called_once()
    mock.PermissionsManager.assert_called_once_with(
        db_client=mock.db_client, user_email=mock.user_email
    )
    mock.permissions_manager_instance.has_permission.assert_called_once_with(
        mock.permission
    )


def test_check_permissions_happy_path(check_permissions_mocks):
    mock = check_permissions_mocks
    mock.permissions_manager_instance.has_permission.return_value = True

    check_permissions(mock.permission)

    assert_pre_conditional_check_permission_mocks(mock)
    mock.abort.assert_not_called()


def test_check_permissions_user_does_not_have_permission(check_permissions_mocks):
    mock = check_permissions_mocks
    mock.permissions_manager_instance.has_permission.return_value = False
    check_permissions(mock.permission)

    assert_pre_conditional_check_permission_mocks(mock)
    mock.abort.assert_called_once_with(
        code=HTTPStatus.FORBIDDEN,
        message="You do not have permission to access this endpoint",
    )


class CheckUserPermissionMocks(DynamicMagicMock):
    db_client: MagicMock
    user_id: MagicMock
    permission: MagicMock
    abort: MagicMock


class GetUserIdFromDatabaseMocks(DynamicMagicMock):
    db_client: MagicMock
    user_id: MagicMock
    api_key: MagicMock


def test_check_api_key_associated_with_user_happy_path(mock_abort):
    mock = GetUserIdFromDatabaseMocks()
    mock.db_client.get_user_by_api_key.return_value = mock.user_id
    check_api_key_associated_with_user(mock.db_client, mock.api_key)
    mock.db_client.get_user_by_api_key.assert_called_once_with(mock.api_key)
    mock_abort.assert_not_called()


def test_check_api_key_associated_with_user_invalid_api_key(mock_abort):
    mock = GetUserIdFromDatabaseMocks()
    mock.db_client.get_user_by_api_key.return_value = None
    check_api_key_associated_with_user(mock.db_client, mock.api_key)
    mock.db_client.get_user_by_api_key.assert_called_once_with(mock.api_key)
    mock_abort.assert_called_once_with(HTTPStatus.UNAUTHORIZED, "Invalid API Key")


class CheckApiKeyMocks(DynamicMagicMock):
    permission: MagicMock
    db_client: MagicMock
    get_db_client: MagicMock
    get_api_key_from_header: MagicMock
    check_api_key_associated_with_user: MagicMock
    api_key: MagicMock


def test_check_api_key():
    mock = CheckApiKeyMocks(
        patch_root=PATCH_ROOT,
        mocks_to_patch=[
            "check_api_key_associated_with_user",
            "get_db_client",
            "get_api_key_from_header",
        ],
    )
    mock.get_api_key_from_header.return_value = mock.api_key
    mock.get_db_client.return_value = mock.db_client

    check_api_key()

    mock.get_api_key_from_header.assert_called_once()
    mock.get_db_client.assert_called_once()
    mock.check_api_key_associated_with_user.assert_called_once_with(
        mock.db_client, mock.api_key
    )
