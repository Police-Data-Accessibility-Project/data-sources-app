import pytest
from unittest.mock import MagicMock, patch, call
from http import HTTPStatus
from flask import Response, make_response

from middleware.custom_exceptions import UserNotFoundError
from middleware.enums import PermissionsEnum, PermissionsActionEnum
from middleware.permissions_logic import (
    PermissionsManager,
    manage_user_permissions,
    update_permissions_wrapper,
)
from tests.helper_scripts.DymamicMagicMock import DynamicMagicMock


class PermissionsManagerMocks(DynamicMagicMock):
    db_client: MagicMock
    make_response: MagicMock
    abort: MagicMock
    user_email: MagicMock


@pytest.fixture
def mock():
    mock = PermissionsManagerMocks(
        patch_root="middleware.permissions_logic",
        mocks_to_patch=["make_response", "abort"],
    )
    mock.db_client.get_user_permissions.return_value = [
        PermissionsEnum.READ_ALL_USER_INFO
    ]
    return mock


def test_permissions_manager_init_success(mock):
    pm = PermissionsManager(mock.db_client, mock.user_email)
    assert pm.db_client == mock.db_client
    assert pm.user_email == mock.user_email
    mock.db_client.get_user_permissions.called_once_with(mock.user_email)
    mock.abort.assert_not_called()


def test_permissions_manager_init_user_not_found(mock):
    mock.db_client.get_user_info.side_effect = UserNotFoundError("User not found")
    PermissionsManager(mock.db_client, mock.user_email)
    mock.db_client.get_user_info.called_once_with(mock.user_email)
    mock.abort.assert_called_once_with(HTTPStatus.NOT_FOUND, "User not found")
    mock.db_client.get_user_permissions.assert_not_called()


def test_get_user_permissions(mock):
    pm = PermissionsManager(mock.db_client, mock.user_email)
    pm.get_user_permissions()
    mock.make_response.assert_called_with(
        [PermissionsEnum.READ_ALL_USER_INFO.value], HTTPStatus.OK
    )


def test_add_user_permission_success(mock):
    pm = PermissionsManager(mock.db_client, mock.user_email)
    pm.add_user_permission(PermissionsEnum.DB_WRITE)
    mock.db_client.add_user_permission.assert_called_with(
        mock.user_email, PermissionsEnum.DB_WRITE
    )
    mock.make_response.assert_called_with("Permission added", HTTPStatus.OK)


def test_add_user_permission_conflict(mock):
    pm = PermissionsManager(mock.db_client, mock.user_email)
    pm.add_user_permission(PermissionsEnum.READ_ALL_USER_INFO)
    mock.make_response.assert_called_with(
        f"Permission {PermissionsEnum.READ_ALL_USER_INFO.value} already exists for user",
        HTTPStatus.CONFLICT,
    )


def test_remove_user_permission_success(mock):
    pm = PermissionsManager(mock.db_client, mock.user_email)
    pm.remove_user_permission(PermissionsEnum.READ_ALL_USER_INFO)
    mock.db_client.remove_user_permission.assert_called_with(
        mock.user_email, PermissionsEnum.READ_ALL_USER_INFO
    )
    mock.make_response.assert_called_with("Permission removed", HTTPStatus.OK)


def test_remove_user_permission_not_found(mock):
    pm = PermissionsManager(mock.db_client, mock.user_email)
    pm.remove_user_permission(PermissionsEnum.DB_WRITE)
    mock.make_response.assert_called_with(
        f"Permission {PermissionsEnum.DB_WRITE.value} does not exist for user. Cannot remove.",
        HTTPStatus.CONFLICT,
    )


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
    db_client: MagicMock
    user_email: MagicMock
    permission_str: MagicMock
    action_str: MagicMock
    permission_enum: MagicMock
    action_enum: MagicMock


def test_update_permissions_wrapper():
    mock = UpdatePermissionsWrapperMock(
        patch_root="middleware.permissions_logic",
        mocks_to_patch=["get_valid_enum_value", "manage_user_permissions"],
    )
    mock.get_valid_enum_value.side_effect = [
        mock.action_enum,
        mock.permission_enum
    ]
    response = update_permissions_wrapper(
        mock.db_client, mock.user_email, mock.permission_str, mock.action_str
    )
    mock.get_valid_enum_value.assert_has_calls(
        [
            call(PermissionsActionEnum, mock.action_str),
            call(PermissionsEnum, mock.permission_str)
        ]
    )
    mock.manage_user_permissions.assert_called_once_with(
        db_client=mock.db_client,
        user_email=mock.user_email,
        method=f"{mock.action_enum.value}_user_permission",
        permission=mock.permission_enum
    )
