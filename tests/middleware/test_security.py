import datetime
import uuid
from http import HTTPStatus
from typing import Callable

import flask
import pytest
from unittest.mock import MagicMock, patch

from flask import Flask

from middleware import security
from middleware.exceptions import InvalidAPIKeyException, InvalidAuthorizationHeaderException
from middleware.security import (
    check_api_key_associated_with_user,
    check_api_key,
    check_permissions,
    INVALID_API_KEY_MESSAGE,
)
from middleware.decorators import api_key_required
from tests.helper_scripts.DynamicMagicMock import DynamicMagicMock
from tests.helper_scripts.common_mocks_and_patches import patch_abort

PATCH_ROOT = "middleware.security"


@pytest.fixture
def dummy_route():
    @api_key_required
    def _dummy_route():
        return "This is a protected route", HTTPStatus.OK.value

    return _dummy_route


DUMMY_AUTHORIZATION = {"Authorization": "Basic valid_api_key"}


@pytest.fixture
def mock_abort(monkeypatch) -> MagicMock:
    return patch_abort(monkeypatch, path=PATCH_ROOT)


class CheckPermissionsMocks(DynamicMagicMock):
    get_jwt_identity: MagicMock
    verify_jwt_in_request: MagicMock
    get_db_client: MagicMock
    PermissionsManager: MagicMock
    abort: MagicMock


@pytest.fixture
def check_permissions_mocks():
    mock = CheckPermissionsMocks(
        patch_root=PATCH_ROOT,
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


def test_check_api_key_associated_with_user_happy_path(mock_abort):
    mock = MagicMock()
    mock.db_client.get_user_by_api_key.return_value = mock.user_id
    check_api_key_associated_with_user(mock.db_client, mock.api_key)
    mock.db_client.get_user_by_api_key.assert_called_once_with(mock.api_key)
    mock_abort.assert_not_called()


def test_check_api_key_associated_with_user_invalid_api_key(mock_abort):
    mock = MagicMock()
    mock.db_client.get_user_by_api_key.return_value = None
    check_api_key_associated_with_user(mock.db_client, mock.api_key)
    mock.db_client.get_user_by_api_key.assert_called_once_with(mock.api_key)
    mock_abort.assert_called_once_with(HTTPStatus.UNAUTHORIZED, "Invalid API Key")


class CheckApiKeyMocks(DynamicMagicMock):
    get_db_client: MagicMock
    get_api_key_from_request_header: MagicMock
    check_api_key_associated_with_user: MagicMock


def test_check_api_key_happy_path():
    mock = CheckApiKeyMocks(
        patch_root=PATCH_ROOT,
    )
    mock.get_api_key_from_request_header.return_value = mock.api_key
    mock.get_db_client.return_value = mock.db_client

    check_api_key()

    mock.get_api_key_from_request_header.assert_called_once()
    mock.get_db_client.assert_called_once()
    mock.check_api_key_associated_with_user.assert_called_once_with(
        mock.db_client, mock.api_key
    )


@pytest.mark.parametrize(
    "exception",
    [
        InvalidAuthorizationHeaderException,
        InvalidAPIKeyException,
    ],
)
def test_check_api_key_invalid_api_key(exception, mock_abort):
    mock = CheckApiKeyMocks(
        patch_root=PATCH_ROOT,
    )
    mock.get_api_key_from_request_header.side_effect = exception

    check_api_key()

    mock.get_api_key_from_request_header.assert_called_once()
    mock.get_db_client.assert_not_called()
    mock.check_api_key_associated_with_user.assert_not_called()
    mock_abort.assert_called_once_with(
        code=HTTPStatus.UNAUTHORIZED, message=INVALID_API_KEY_MESSAGE
    )
