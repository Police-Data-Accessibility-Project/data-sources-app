from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from werkzeug.exceptions import Forbidden

from middleware.decorators.api_key_required import api_key_required
from middleware.security.helpers import (
    check_permissions,
)
from tests.helpers.DynamicMagicMock import DynamicMagicMock

PATCH_ROOT = "middleware.security.helpers"


@pytest.fixture
def dummy_route():
    @api_key_required
    def _dummy_route():
        return "This is a protected route", HTTPStatus.OK.value

    return _dummy_route


DUMMY_AUTHORIZATION = {"Authorization": "Basic valid_api_key"}


class CheckPermissionsMocks(DynamicMagicMock):
    get_jwt_identity: MagicMock
    verify_jwt_in_request: MagicMock
    DatabaseClient: MagicMock
    PermissionsManager: MagicMock


@pytest.fixture
def check_permissions_mocks():
    mock = CheckPermissionsMocks(
        patch_root=PATCH_ROOT,
    )
    mock.get_jwt_identity.return_value = {"user_email": mock.user_email, "id": mock.id}
    mock.DatabaseClient.return_value = mock.db_client
    mock.PermissionsManager.return_value = mock.permissions_manager_instance
    return mock


def assert_pre_conditional_check_permission_mocks(mock: CheckPermissionsMocks):
    mock.verify_jwt_in_request.assert_called_once()
    mock.get_jwt_identity.assert_called_once()
    mock.DatabaseClient.assert_called_once()
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


def test_check_permissions_user_does_not_have_permission(check_permissions_mocks):
    mock = check_permissions_mocks
    mock.permissions_manager_instance.has_permission.return_value = False
    with pytest.raises(Forbidden):
        check_permissions(mock.permission)

    assert_pre_conditional_check_permission_mocks(mock)
