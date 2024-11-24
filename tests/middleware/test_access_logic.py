from unittest.mock import MagicMock

import pytest

from middleware.access_logic import (
    get_authorization_header_from_request,
    get_key_from_authorization_header,
    AccessInfoPrimary,
    check_permissions_with_access_info,
    get_user_email_from_api_key,
    get_jwt_access_info_with_permissions,
)
from middleware.exceptions import (
    InvalidAPIKeyException,
    InvalidAuthorizationHeaderException,
)
from middleware.enums import PermissionsEnum, AccessTypeEnum
from tests.helper_scripts.DynamicMagicMock import DynamicMagicMock
from tests.helper_scripts.common_mocks_and_patches import (
    patch_request_headers,
    patch_abort,
)


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
    assert "api_key" == get_key_from_authorization_header("Basic api_key")


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
        get_key_from_authorization_header(authorization_header)


class GetAPIKeyFromRequestHeaderMock(DynamicMagicMock):
    get_authorization_header_from_request: MagicMock
    get_api_key_from_authorization_header: MagicMock


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
            AccessInfoPrimary(
                user_email="test_email",
                access_type=AccessTypeEnum.JWT,
                permissions=[PermissionsEnum.READ_ALL_USER_INFO],
            ),
            [PermissionsEnum.READ_ALL_USER_INFO],
            False,
        ),
        (
            AccessInfoPrimary(
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
    ),
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
    "get_api_key_from_request_header_result, "
    "get_api_key_from_request_header_side_effect, "
    "raises_exception,"
    "expected_result",
    (
        # Happy path
        ("test_api_key", None, False, MagicMock()),
        (None, InvalidAPIKeyException, True, None),
        (None, InvalidAuthorizationHeaderException, True, None),
    ),
)
def test_get_user_email_from_api_key(
    get_api_key_from_request_header_result,
    get_api_key_from_request_header_side_effect,
    raises_exception,
    expected_result,
    monkeypatch,
):

    mock_get_api_key_from_request_header = MagicMock(
        return_value=get_api_key_from_request_header_result
    )
    if raises_exception:
        mock_get_api_key_from_request_header.side_effect = (
            get_api_key_from_request_header_side_effect
        )
    monkeypatch.setattr(
        "middleware.access_logic.get_api_key_from_request_header",
        mock_get_api_key_from_request_header,
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
