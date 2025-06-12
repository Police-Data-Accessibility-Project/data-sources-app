from unittest.mock import MagicMock

import pytest

from middleware.security.access_logic import (
    get_authorization_header_from_request,
)
from middleware.security.api_key.helpers import get_key_from_authorization_header
from middleware.security.auth.method_config.helpers import (
    check_permissions_with_access_info,
)
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.enums import PermissionsEnum, AccessTypeEnum
from tests.helper_scripts.DynamicMagicMock import DynamicMagicMock
from tests.helper_scripts.common_mocks_and_patches import (
    patch_request_headers,
)


def test_get_authorization_header_from_request_happy_path(monkeypatch):
    patch_request_headers(
        monkeypatch,
        path="middleware.security.access_logic",
        request_headers={"Authorization": "Basic api_key"},
    )
    assert "Basic api_key" == get_authorization_header_from_request()


def test_get_api_key_from_authorization_header_happy_path(monkeypatch):
    assert "api_key" == get_key_from_authorization_header("Basic api_key")


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
        "middleware.flask_response_manager.FlaskResponseManager.permission_denied_abort",
        mock_permission_denied_abort,
    )
    check_permissions_with_access_info(access_info, permissions)

    if permission_denied_abort_called:
        mock_permission_denied_abort.assert_called_once()
    else:
        mock_permission_denied_abort.assert_not_called()
