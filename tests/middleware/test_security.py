from http import HTTPStatus

import pytest
from unittest.mock import MagicMock

from middleware.security.helpers import (
    check_permissions,
)
from middleware.decorators.api_key_required import api_key_required
from tests.helper_scripts.DynamicMagicMock import DynamicMagicMock
from tests.helper_scripts.common_mocks_and_patches import patch_abort

PATCH_ROOT = "middleware.security.helpers"


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
    mock.get_jwt_identity.return_value = {"user_email": mock.user_email, "id": mock.id}
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
