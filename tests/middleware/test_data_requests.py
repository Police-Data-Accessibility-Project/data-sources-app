from http import HTTPStatus
from typing import Optional
from unittest.mock import MagicMock, patch, call

import pytest

from database_client.database_client import DatabaseClient
from database_client.db_client_dataclasses import WhereMapping
from database_client.enums import RelationRoleEnum, ColumnPermissionEnum
from middleware.access_logic import AccessInfo
from middleware.enums import AccessTypeEnum, PermissionsEnum
from middleware.primary_resource_logic.data_requests import (
    get_data_requests_relation_role,
    RELATION,
    get_formatted_data_requests,
    get_standard_and_owner_zipped_data_requests,
    allowed_to_delete_request,
    get_data_requests_wrapper,
    get_data_requests_with_permitted_columns,
)
from tests.helper_scripts.DynamicMagicMock import DynamicMagicMock
from tests.helper_scripts.common_mocks_and_patches import (
    patch_and_return_mock,
)

PATCH_ROOT = "middleware.primary_resource_logic.data_requests"


@pytest.mark.parametrize(
    "access_type, is_owner, permissions, data_request_id, expected_relation_role",
    (
        (AccessTypeEnum.API_KEY, False, [], 1, RelationRoleEnum.STANDARD),
        (AccessTypeEnum.JWT, False, [], 1, RelationRoleEnum.STANDARD),
        (
            AccessTypeEnum.JWT,
            False,
            [PermissionsEnum.DB_WRITE],
            1,
            RelationRoleEnum.ADMIN,
        ),
        (AccessTypeEnum.JWT, True, [], 1, RelationRoleEnum.OWNER),
        (
            AccessTypeEnum.JWT,
            False,
            [PermissionsEnum.READ_ALL_USER_INFO],
            None,
            RelationRoleEnum.STANDARD,
        ),
    ),
)
def test_get_data_requests_relation_role(
    access_type: AccessTypeEnum,
    is_owner: bool,
    permissions: list[PermissionsEnum],
    data_request_id: Optional[int],
    expected_relation_role: RelationRoleEnum,
):
    mock = MagicMock()
    mock.db_client.user_is_creator_of_data_request.return_value = is_owner
    relation_role = get_data_requests_relation_role(
        db_client=mock.db_client,
        data_request_id=data_request_id,
        access_info=AccessInfo(
            user_email="test_user", access_type=access_type, permissions=permissions
        ),
    )
    assert relation_role == expected_relation_role


@pytest.fixture
def mock_check_has_permission_to_edit_columns(monkeypatch):
    return patch_and_return_mock(
        f"{PATCH_ROOT}.check_has_permission_to_edit_columns", monkeypatch
    )


@pytest.fixture
def mock_get_data_requests_relation_role(monkeypatch):
    return patch_and_return_mock(
        f"{PATCH_ROOT}.get_data_requests_relation_role", monkeypatch
    )


@pytest.fixture
def mock_message_response(monkeypatch):
    return patch_and_return_mock(f"{PATCH_ROOT}.message_response", monkeypatch)


@pytest.fixture
def mock_get_data_requests_with_permitted_columns(monkeypatch):
    return patch_and_return_mock(f"{PATCH_ROOT}.get_data_requests_with_permitted_columns", monkeypatch)

@patch(PATCH_ROOT + ".format_list_response")
@patch(PATCH_ROOT + ".get_formatted_data_requests")
def test_get_data_requests_wrapper(
    mock_get_formatted_data_requests: MagicMock,
    mock_format_list_response: MagicMock,
    mock_get_data_requests_relation_role,
    mock_make_response,
    monkeypatch,
):
    mock = MagicMock()
    get_data_requests_wrapper(mock.db_client, mock.access_info)

    mock_get_data_requests_relation_role.assert_called_once_with(
        mock.db_client, data_request_id=None, access_info=mock.access_info
    )
    mock_get_formatted_data_requests.assert_called_once_with(
        mock.access_info,
        mock.db_client,
        mock_get_data_requests_relation_role.return_value,
    )

    mock_format_list_response.assert_called_once_with(
        mock_get_formatted_data_requests.return_value
    )

    mock_make_response.assert_called_once_with(
        mock_format_list_response.return_value,
        HTTPStatus.OK,
    )


class GetFormattedDataRequestsMocks(DynamicMagicMock):
    get_standard_and_owner_zipped_data_requests: MagicMock
    get_data_requests_with_permitted_columns: MagicMock


@pytest.fixture
def get_formatted_data_requests_mocks():
    return GetFormattedDataRequestsMocks(
        patch_root=PATCH_ROOT,
    )


@patch(PATCH_ROOT + ".get_permitted_columns")
def test_get_data_requests_with_permitted_columns(
    mock_get_permitted_columns: MagicMock,
):
    mock = MagicMock()

    results = get_data_requests_with_permitted_columns(
        db_client=mock.db_client,
        relation_role=mock.relation_role,
        where_mappings=mock.where_mappings,
    )


    assert results == mock.db_client.get_data_requests.return_value


    # assert results == mock.zipped_data_requests

    mock_get_permitted_columns.assert_called_once_with(
        db_client=mock.db_client,
        relation=RELATION,
        role=mock.relation_role,
        column_permission=ColumnPermissionEnum.READ,
    )
    mock.db_client.get_data_requests.assert_called_once_with(
        columns=mock_get_permitted_columns.return_value,
        where_mappings=mock.where_mappings,
    )



def test_get_formatted_data_requests_admin(get_formatted_data_requests_mocks):
    mock = get_formatted_data_requests_mocks

    get_formatted_data_requests(
        db_client=mock.db_client,
        access_info=mock.access_info,
        relation_role=RelationRoleEnum.ADMIN,
    )
    mock.get_data_requests_with_permitted_columns.assert_called_once_with(
        mock.db_client, RelationRoleEnum.ADMIN
    )
    mock.get_standard_and_owner_zipped_data_requests.assert_not_called()


def test_get_formatted_data_requests_standard(get_formatted_data_requests_mocks):
    mock = get_formatted_data_requests_mocks

    get_formatted_data_requests(
        db_client=mock.db_client,
        access_info=mock.access_info,
        relation_role=RelationRoleEnum.STANDARD,
    )
    mock.get_data_requests_with_permitted_columns.assert_not_called()
    mock.get_standard_and_owner_zipped_data_requests.assert_called_once_with(
        mock.access_info.user_email, mock.db_client
    )


def test_get_formatted_data_requests_owner(get_formatted_data_requests_mocks):
    mock = get_formatted_data_requests_mocks

    with pytest.raises(ValueError):
        get_formatted_data_requests(
            db_client=mock.db_client,
            access_info=mock.access_info,
            relation_role=RelationRoleEnum.OWNER,
        )
    mock.get_data_requests_with_permitted_columns.assert_not_called()
    mock.get_standard_and_owner_zipped_data_requests.assert_not_called()


def test_get_standard_and_owner_zipped_data_requests(
        mock_get_data_requests_with_permitted_columns: MagicMock,
):
    mock = MagicMock()
    mock_get_data_requests_with_permitted_columns.side_effect = [
        [mock.data_request_standard],
        [mock.data_request_owner],
    ]
    mock.db_client.get_user_id.return_value = mock.user_id
    zipped_data_requests = get_standard_and_owner_zipped_data_requests(
        user_email=mock.user_email, db_client=mock.db_client
    )
    assert zipped_data_requests == [mock.data_request_owner, mock.data_request_standard]
    neq_expected_mapping = [WhereMapping(column="creator_user_id", eq=False, value=mock.user_id)]
    eq_expected_mapping = [WhereMapping(column="creator_user_id", value=mock.user_id)]
    mock_get_data_requests_with_permitted_columns.assert_has_calls(
        [
            call(
                db_client=mock.db_client,
                relation_role=RelationRoleEnum.STANDARD,
                where_mappings=neq_expected_mapping,
            ),
            call(
                db_client=mock.db_client,
                relation_role=RelationRoleEnum.OWNER,
                where_mappings=eq_expected_mapping,
            ),
        ],
        any_order=True,
    )


@pytest.fixture
def mock_abort(monkeypatch):
    return patch_and_return_mock(f"{PATCH_ROOT}.abort", monkeypatch)


@pytest.fixture
def mock_make_response(monkeypatch):
    return patch_and_return_mock(f"{PATCH_ROOT}.make_response", monkeypatch)

def check_allowed_to_delete_request_mock_calls(mock: MagicMock):
    mock.db_client.get_user_id.assert_called_once_with(mock.access_info.user_email)
    mock.db_client.user_is_creator_of_data_request.assert_called_once_with(
        user_id=mock.db_client.get_user_id.return_value,
        data_request_id=mock.data_request_id,
    )

def test_allowed_to_delete_request_user_is_creator():
    mock = MagicMock()
    mock.db_client.user_is_creator_of_data_request.return_value = True
    mock.access_info.permissions = []
    assert allowed_to_delete_request(
        access_info=mock.access_info,
        data_request_id=mock.data_request_id,
        db_client=mock.db_client,
    )
    check_allowed_to_delete_request_mock_calls(mock)


def test_allowed_to_delete_request_has_permissions():
    mock = MagicMock()
    mock.db_client.user_is_creator_of_data_request.return_value = False
    mock.access_info.permissions = [PermissionsEnum.DB_WRITE]
    assert allowed_to_delete_request(
        access_info=mock.access_info,
        data_request_id=mock.data_request_id,
        db_client=mock.db_client,
    )
    check_allowed_to_delete_request_mock_calls(mock)


#
def test_allowed_to_delete_request_user_not_creator_and_without_permissions():
    mock = MagicMock()
    mock.access_info.permissions = []
    mock.db_client.user_is_creator_of_data_request.return_value = False
    assert (
        allowed_to_delete_request(
            access_info=mock.access_info,
            data_request_id=mock.data_request_id,
            db_client=mock.db_client,
        )
        is False
    )
    check_allowed_to_delete_request_mock_calls(mock)
