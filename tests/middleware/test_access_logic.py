from dataclasses import dataclass
from http import HTTPStatus
from unittest.mock import MagicMock

import pytest

from middleware.access_logic import (
    get_authorization_header_from_request,
    get_api_key_from_authorization_header,
    get_api_key_from_request_header,
    JWT_OR_API_KEY_NEEDED_ERROR_MESSAGE, AccessInfo, check_permissions_with_access_info, try_api_key_authentication,
    try_jwt_authentication, get_authentication, get_authentication_error_message, get_user_email_from_api_key,
    get_access_info_from_jwt, get_jwt_access_info_with_permissions,
)
from middleware.exceptions import InvalidAPIKeyException, InvalidAuthorizationHeaderException
from middleware.enums import PermissionsEnum, AccessTypeEnum
from middleware.security import check_permissions
from tests.helper_scripts.DynamicMagicMock import DynamicMagicMock
from tests.helper_scripts.common_mocks_and_patches import patch_request_headers, patch_abort


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

@pytest.mark.parametrize(
    "access_info, permissions, permission_denied_abort_called",
    (
        (
            AccessInfo(
                user_email="test_email",
                access_type=AccessTypeEnum.JWT,
                permissions=[PermissionsEnum.READ_ALL_USER_INFO],
            ),
            [PermissionsEnum.READ_ALL_USER_INFO],
            False,
        ),
        (
            AccessInfo(
                user_email="test_email",
                access_type=AccessTypeEnum.JWT,
                permissions=[PermissionsEnum.READ_ALL_USER_INFO],
            ),
            [PermissionsEnum.READ_ALL_USER_INFO, PermissionsEnum.DB_WRITE],
            True,
        ),
        (
            None,
            None,
            True,
        ),
    )
)
def test_check_permissions_with_access_info(
    access_info, permissions, permission_denied_abort_called, monkeypatch
):

    mock_permission_denied_abort = MagicMock()
    monkeypatch.setattr(
        "middleware.access_logic.permission_denied_abort", mock_permission_denied_abort
    )
    check_permissions_with_access_info(access_info, permissions)

    if permission_denied_abort_called:
        mock_permission_denied_abort.assert_called_once()
    else:
        mock_permission_denied_abort.assert_not_called()


@pytest.mark.parametrize(
    "allowed_access_methods, get_user_email_result, expected_result",
    (
        # Happy path
        (
            [AccessTypeEnum.API_KEY, AccessTypeEnum.JWT],
            "test_email",
            AccessInfo(
                user_email="test_email",
                access_type=AccessTypeEnum.API_KEY,
            )
        ),
        (
            [AccessTypeEnum.JWT],
            "test_email",
            None,
        ),
        (
            [AccessTypeEnum.API_KEY],
            None,
            None,
        )
    )
)
def test_try_api_key_authentication(
    allowed_access_methods, get_user_email_result, expected_result, monkeypatch
):

    mock_get_user_email = MagicMock(return_value=get_user_email_result)
    monkeypatch.setattr(
        "middleware.access_logic.get_user_email_from_api_key", mock_get_user_email
    )

    result = try_api_key_authentication(allowed_access_methods)

    if (AccessTypeEnum.API_KEY in allowed_access_methods):
        mock_get_user_email.assert_called_once()
    else:
        mock_get_user_email.assert_not_called()
    assert result == expected_result


@pytest.mark.parametrize(
    "allowed_access_methods, restrict_to_permissions, "
    "get_access_info_result, expected_result, "
    "check_permissions_called, get_access_info_called",
    (
        # Happy path
        (
            [AccessTypeEnum.JWT],
            [PermissionsEnum.READ_ALL_USER_INFO],
            AccessInfo(
                user_email="test_email",
                access_type=AccessTypeEnum.JWT,
                permissions=[PermissionsEnum.READ_ALL_USER_INFO],
            ),
            AccessInfo(
                user_email="test_email",
                access_type=AccessTypeEnum.JWT,
                permissions=[PermissionsEnum.READ_ALL_USER_INFO],
            ),
            True,
            True
        ),
        (
            [AccessTypeEnum.JWT],
            [PermissionsEnum.READ_ALL_USER_INFO],
            None,
            None,
            False,
            True
        ),
        (
            [AccessTypeEnum.JWT],
            None,
            AccessInfo(
                user_email="test_email",
                access_type=AccessTypeEnum.JWT,
                permissions=[PermissionsEnum.READ_ALL_USER_INFO],
            ),
            AccessInfo(
                user_email="test_email",
                access_type=AccessTypeEnum.JWT,
                permissions=[PermissionsEnum.READ_ALL_USER_INFO],
            ),
            False,
            True
        ),
        (
            [AccessTypeEnum.API_KEY],
            None,
            None,
            None,
            False,
            False
        ),
    )
)
def test_try_jwt_authentication(
    allowed_access_methods,
    restrict_to_permissions,
    get_access_info_result,
    expected_result,
    check_permissions_called,
    get_access_info_called,
    monkeypatch
):

    mock_get_access_info = MagicMock(return_value=get_access_info_result)
    monkeypatch.setattr(
        "middleware.access_logic.get_access_info_from_jwt", mock_get_access_info
    )
    mock_check_permissions = MagicMock()
    monkeypatch.setattr(
        "middleware.access_logic.check_permissions_with_access_info", mock_check_permissions
    )

    result = try_jwt_authentication(
        allowed_access_methods,
        restrict_to_permissions
    )

    assert result == expected_result

    if check_permissions_called:
        mock_check_permissions.assert_called_once_with(
            mock_get_access_info.return_value,
            restrict_to_permissions
        )
    else:
        mock_check_permissions.assert_not_called()
    if get_access_info_called:
        mock_get_access_info.assert_called_once()
    else:
        mock_get_access_info.assert_not_called()

@pytest.mark.parametrize(
    "try_api_key_authentication_result, try_jwt_authentication_result, expected_result, mock_abort_called",
    (
        # Happy path
        (
            AccessInfo(
                user_email="test_email",
                access_type=AccessTypeEnum.API_KEY,
                permissions=[PermissionsEnum.READ_ALL_USER_INFO],
            ),
            None,
            AccessInfo(
                user_email="test_email",
                access_type=AccessTypeEnum.API_KEY,
                permissions=[PermissionsEnum.READ_ALL_USER_INFO],
            ),
            False
        ),
        (
            None,
            AccessInfo(
                user_email="test_email",
                access_type=AccessTypeEnum.JWT,
                permissions=[PermissionsEnum.READ_ALL_USER_INFO],
            ),
            AccessInfo(
                user_email="test_email",
                access_type=AccessTypeEnum.JWT,
                permissions=[PermissionsEnum.READ_ALL_USER_INFO],
            ),
            False
        ),
        (
            None,
            None,
            None,
            True
        ),
    )
)
def test_get_authentication(
    try_api_key_authentication_result,
    try_jwt_authentication_result,
    expected_result,
    mock_abort_called,
    monkeypatch
):

    monkeypatch.setattr(
        "middleware.access_logic.try_api_key_authentication", MagicMock(return_value=try_api_key_authentication_result)
    )

    monkeypatch.setattr(
        "middleware.access_logic.try_jwt_authentication", MagicMock(return_value=try_jwt_authentication_result)
    )

    mock_abort = patch_abort(monkeypatch, path="middleware.access_logic")

    mock_get_authentication_error_message = MagicMock(return_value="test_error_message")
    monkeypatch.setattr(
        "middleware.access_logic.get_authentication_error_message", mock_get_authentication_error_message
    )

    mock = MagicMock()

    result = get_authentication(
        mock.allowed_access_methods,
        mock.restrict_to_permissions
    )

    assert result == expected_result

    if mock_abort_called:
        mock_get_authentication_error_message.assert_called_once_with(mock.allowed_access_methods)
        mock_abort.assert_called_once_with(
            HTTPStatus.UNAUTHORIZED,
            message=mock_get_authentication_error_message.return_value
        )
    else:
        mock_abort.assert_not_called()


@pytest.mark.parametrize(
    "get_api_key_from_request_header_result, "
    "get_api_key_from_request_header_side_effect, "
    "raises_exception,"
    "expected_result",
    (
        # Happy path
        (
            "test_api_key",
            None,
            False,
            MagicMock()
        ),
        (
            None,
            InvalidAPIKeyException,
            True,
            None
        ),
        (
            None,
            InvalidAuthorizationHeaderException,
            True,
            None
        ),
    )
)
def test_get_user_email_from_api_key(
    get_api_key_from_request_header_result,
    get_api_key_from_request_header_side_effect,
    raises_exception,
    expected_result,
    monkeypatch
):

    mock_get_api_key_from_request_header = MagicMock(return_value=get_api_key_from_request_header_result)
    if raises_exception:
        mock_get_api_key_from_request_header.side_effect = get_api_key_from_request_header_side_effect
    monkeypatch.setattr(
        "middleware.access_logic.get_api_key_from_request_header", mock_get_api_key_from_request_header
    )

    mock = MagicMock()

    monkeypatch.setattr(
        "middleware.access_logic.get_db_client", MagicMock(return_value=mock.db_client)
    )

    if not raises_exception:
        mock.db_client.get_user_by_api_key.return_value = expected_result

    result = get_user_email_from_api_key()

    if raises_exception:
        assert result is None
    else:
        assert result == expected_result.email

@pytest.mark.parametrize(
    "verify_jwt_in_request_result, "
    "get_jwt_identity_result, "
    "get_jwt_access_info_with_permissions_called",
    (
        # Happy path
        (
            MagicMock(),
            None,
            False
        ),
        (
            None,
            MagicMock(),
            False
        ),
        (
            MagicMock(),
            MagicMock(),
            True
        ),
    )
)
def test_get_access_info_from_jwt(
    verify_jwt_in_request_result,
    get_jwt_identity_result,
    get_jwt_access_info_with_permissions_called,
    monkeypatch
):

    mock_verify_jwt_in_request = MagicMock(return_value=verify_jwt_in_request_result)
    mock_get_jwt_identity = MagicMock(return_value=get_jwt_identity_result)
    mock_get_jwt_access_info_with_permissions = MagicMock()
    monkeypatch.setattr(
        "middleware.access_logic.verify_jwt_in_request", mock_verify_jwt_in_request
    )
    monkeypatch.setattr(
        "middleware.access_logic.get_jwt_identity", mock_get_jwt_identity
    )
    monkeypatch.setattr(
        "middleware.access_logic.get_jwt_access_info_with_permissions", mock_get_jwt_access_info_with_permissions
    )

    mock = MagicMock()

    monkeypatch.setattr(
        "middleware.access_logic.get_db_client", MagicMock(return_value=mock.db_client)
    )

    result = get_access_info_from_jwt()

    if get_jwt_access_info_with_permissions_called:
        assert result == mock_get_jwt_access_info_with_permissions.return_value
        mock_get_jwt_access_info_with_permissions.assert_called_once_with(mock_get_jwt_identity.return_value)
    else:
        assert result is None
        mock_get_jwt_access_info_with_permissions.assert_not_called()

def test_get_jwt_access_info_with_permissions(
    monkeypatch
):

    mock = MagicMock()
    mock.get_user_permissions.return_value = mock.permissions

    monkeypatch.setattr(
        "middleware.access_logic.get_user_permissions", mock.get_user_permissions
    )

    result = get_jwt_access_info_with_permissions(mock.user_email)

    mock.get_user_permissions.assert_called_once_with(mock.user_email)

    assert result == AccessInfo(
        user_email=mock.user_email,
        access_type=AccessTypeEnum.JWT,
        permissions=mock.permissions
    )

