from http import HTTPStatus
from unittest.mock import MagicMock, patch, call

import pytest
from flask import Response
from werkzeug.exceptions import BadRequest, Conflict

from middleware.enums import PermissionsEnum, PermissionsActionEnum
from middleware.exceptions import UserNotFoundError
from middleware.primary_resource_logic.permissions import (
    PermissionsManager,
    manage_user_permissions,
    update_permissions_wrapper,
)
from tests.helper_scripts.DynamicMagicMock import DynamicMagicMock

PATCH_ROOT = "middleware.primary_resource_logic.permissions"


class PermissionsManagerMocks(DynamicMagicMock):
    make_response: MagicMock
    message_response: MagicMock


@pytest.fixture
def mock():
    mock = PermissionsManagerMocks(
        patch_root=PATCH_ROOT,
    )
    mock.db_client.get_user_permissions.return_value = [
        PermissionsEnum.READ_ALL_USER_INFO
    ]
    return mock


def test_permissions_manager_init_user_not_found(mock):
    mock.db_client.get_user_info.side_effect = UserNotFoundError("User not found")
    with pytest.raises(BadRequest):
        PermissionsManager(mock.db_client, mock.user_email)
    mock.db_client.get_user_info.assert_called_once_with(mock.user_email)
    mock.db_client.get_user_permissions.assert_not_called()


def test_get_user_permissions(mock):
    pm = PermissionsManager(mock.db_client, mock.user_email)
    pm.get_user_permissions()
    mock.make_response.assert_called_with(
        [PermissionsEnum.READ_ALL_USER_INFO.value], HTTPStatus.OK
    )


def test_add_user_permission_conflict(mock):
    pm = PermissionsManager(mock.db_client, mock.user_email)

    with pytest.raises(Conflict):
        pm.add_user_permission(PermissionsEnum.READ_ALL_USER_INFO)


def test_remove_user_permission_not_found(mock):
    pm = PermissionsManager(mock.db_client, mock.user_email)

    with pytest.raises(Conflict):
        pm.remove_user_permission(PermissionsEnum.DB_WRITE)


@pytest.fixture
def db_client_mock():
    return MagicMock()


@pytest.fixture
def user_email():
    return "test@example.com"


@pytest.mark.parametrize(
    "method_name, method_arg, expected_response_text, expected_status_code",
    [
        ("get_user_permissions", [], "['READ']", HTTPStatus.OK),
        (
            "add_user_permission",
            [PermissionsEnum.DB_WRITE],
            "Permission added",
            HTTPStatus.OK,
        ),
        (
            "remove_user_permission",
            [PermissionsEnum.READ_ALL_USER_INFO],
            "Permission removed",
            HTTPStatus.OK,
        ),
    ],
)
def test_manage_user_permissions(
    db_client_mock,
    user_email,
    method_name,
    method_arg,
    expected_response_text,
    expected_status_code,
):
    with patch.object(
        PermissionsManager,
        method_name,
        return_value=Response(expected_response_text, status=expected_status_code),
    ) as mock_method:
        response = manage_user_permissions(
            db_client_mock, user_email, method_name, *method_arg
        )
        mock_method.assert_called_once_with(*method_arg)
        assert response.status_code == expected_status_code
        assert response.get_data(as_text=True) == expected_response_text


def test_manage_user_permissions_invalid_method(db_client_mock, user_email):
    with pytest.raises(
        AttributeError,
        match="Method invalid_method does not exist in PermissionsManager",
    ):
        manage_user_permissions(db_client_mock, user_email, "invalid_method")


class UpdatePermissionsWrapperMock(DynamicMagicMock):
    get_valid_enum_value: MagicMock
    manage_user_permissions: MagicMock


def test_update_permissions_wrapper():
    mock = UpdatePermissionsWrapperMock(
        patch_root=PATCH_ROOT,
    )
    mock.get_valid_enum_value.side_effect = [mock.action_enum, mock.permission_enum]
    update_permissions_wrapper(mock.db_client, mock.dto)
    mock.get_valid_enum_value.assert_has_calls(
        [
            call(PermissionsActionEnum, mock.dto.action),
            call(PermissionsEnum, mock.dto.permission),
        ]
    )
    mock.manage_user_permissions.assert_called_once_with(
        db_client=mock.db_client,
        user_email=mock.dto.user_email,
        method=f"{mock.action_enum.value}_user_permission",
        permission=mock.permission_enum,
    )
