from dataclasses import dataclass
from http import HTTPStatus
from unittest.mock import MagicMock

import pytest

from middleware.access_logic import (
    get_authorization_header_from_request,
    InvalidAuthorizationHeaderException,
    get_api_key_from_authorization_header,
    InvalidAPIKeyException,
    get_api_key_from_request_header,
    get_access_info_from_jwt_or_api_key,
    AccessTypeEnum,
    JWT_OR_API_KEY_NEEDED_ERROR_MESSAGE,
)
from middleware.enums import PermissionsEnum
from tests.helper_scripts.DynamicMagicMock import DynamicMagicMock
from tests.helper_scripts.common_mocks_and_patches import patch_request_headers


def test_get_authorization_header_from_request_happy_path(monkeypatch):
    patch_request_headers(
        monkeypatch,
        path="middleware.access_logic",
        request_headers={"Authorization": "Basic api_key"},
    )
    assert "Basic api_key" == get_authorization_header_from_request()


@pytest.mark.parametrize(
    "request_headers",
    [
        {},
        {"Authrztn": "Basic api_key"},
    ],
)
def test_get_authorization_header_from_request_invalid_authorization_header(
    monkeypatch, request_headers
):
    patch_request_headers(
        monkeypatch,
        path="middleware.access_logic",
        request_headers=request_headers,
    )
    with pytest.raises(InvalidAuthorizationHeaderException):
        get_authorization_header_from_request()


def test_get_api_key_from_authorization_header_happy_path(monkeypatch):
    assert "api_key" == get_api_key_from_authorization_header("Basic api_key")


@pytest.mark.parametrize(
    "authorization_header",
    [
        None,
        "Basic",
        "Bearer api_key",
    ],
)
def test_get_api_key_from_authorization_header_invalid_authorization_header(
    monkeypatch, authorization_header
):
    with pytest.raises(InvalidAPIKeyException):
        get_api_key_from_authorization_header(authorization_header)


class GetAPIKeyFromRequestHeaderMock(DynamicMagicMock):
    get_authorization_header_from_request: MagicMock
    get_api_key_from_authorization_header: MagicMock


def test_get_api_key_from_request_header():
    mock = GetAPIKeyFromRequestHeaderMock(
        patch_root="middleware.access_logic",
    )

    result = get_api_key_from_request_header()

    mock.get_authorization_header_from_request.assert_called_once()
    mock.get_api_key_from_authorization_header.assert_called_once_with(
        mock.get_authorization_header_from_request.return_value
    )
    assert result == mock.get_api_key_from_authorization_header.return_value


class GetAccessInfoFromJWTOrAPIKeyMocks(DynamicMagicMock):
    get_user_email_from_api_key: MagicMock
    get_jwt_identity: MagicMock
    AccessInfo: MagicMock
    get_user_permissions: MagicMock
    abort: MagicMock


@pytest.fixture
def get_access_info_mocks():
    return GetAccessInfoFromJWTOrAPIKeyMocks(
        patch_root="middleware.access_logic",
    )


def test_get_access_info_from_jwt_or_api_key_api_key_path(get_access_info_mocks):
    mock = get_access_info_mocks

    mock.get_user_email_from_api_key.return_value = "test_email"

    result = get_access_info_from_jwt_or_api_key()

    mock.get_user_email_from_api_key.assert_called_once()
    mock.get_jwt_identity.assert_not_called()
    mock.AccessInfo.assert_called_once_with(
        user_email="test_email", access_type=AccessTypeEnum.API_KEY
    )
    mock.abort.assert_not_called()
    mock.get_user_permissions.assert_not_called()
    assert result == mock.AccessInfo.return_value


def test_get_access_info_from_jwt_or_api_key_jwt_path(get_access_info_mocks):
    mock = get_access_info_mocks

    mock.get_user_email_from_api_key.return_value = None
    mock.get_jwt_identity.return_value = "test_email"
    mock.get_user_permissions.return_value = [
        PermissionsEnum.READ_ALL_USER_INFO,
        PermissionsEnum.DB_WRITE,
    ]

    result = get_access_info_from_jwt_or_api_key()

    mock.get_user_email_from_api_key.assert_called_once()
    mock.get_jwt_identity.assert_called_once()
    mock.AccessInfo.assert_called_once_with(
        user_email=mock.get_jwt_identity.return_value,
        access_type=AccessTypeEnum.JWT,
        permissions=mock.get_user_permissions.return_value,
    )
    mock.abort.assert_not_called()
    assert result == mock.AccessInfo.return_value


def test_get_access_info_from_jwt_or_api_key_neither(get_access_info_mocks):
    mock = get_access_info_mocks
    mock.get_user_email_from_api_key.return_value = None
    mock.get_jwt_identity.return_value = None

    get_access_info_from_jwt_or_api_key()

    mock.get_user_email_from_api_key.assert_called_once()
    mock.get_jwt_identity.assert_called_once()
    mock.AccessInfo.assert_not_called()
    mock.abort.assert_called_once_with(
        code=HTTPStatus.UNAUTHORIZED, message=JWT_OR_API_KEY_NEEDED_ERROR_MESSAGE
    )
