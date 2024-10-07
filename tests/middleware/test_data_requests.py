from http import HTTPStatus
from typing import Optional
from unittest.mock import MagicMock, patch, call

import pytest

from database_client.db_client_dataclasses import WhereMapping, OrderByParameters
from database_client.enums import RelationRoleEnum, ColumnPermissionEnum
from middleware.access_logic import AccessInfo
from middleware.enums import AccessTypeEnum, PermissionsEnum, Relations
from middleware.primary_resource_logic.data_requests import (
    get_data_requests_relation_role,
    RELATION,
    allowed_to_delete_request,
    get_data_requests_wrapper,
    get_data_requests_with_permitted_columns,
    RelatedSourceByIDDTO,
    delete_data_request_related_source,
)
from tests.helper_scripts.DynamicMagicMock import DynamicMagicMock
from tests.helper_scripts.common_mocks_and_patches import (
    patch_and_return_mock,
)
from tests.conftest import FakeAbort, mock_flask_response_manager

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


class GetFormattedDataRequestsMocks(DynamicMagicMock):
    get_standard_and_owner_zipped_data_requests: MagicMock
    get_data_requests_with_permitted_columns: MagicMock


def check_allowed_to_delete_request_mock_calls(mock: MagicMock):
    mock.db_client.get_user_id.assert_called_once_with(
        email=mock.access_info.user_email
    )
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


@pytest.fixture
def data_request_delete_related_source_mocks(
    mock_flask_response_manager: MagicMock, monkeypatch
):
    mock = MagicMock()
    mock.flask_response_manager = mock_flask_response_manager
    monkeypatch.setattr(mock, f"{PATCH_ROOT}.DatabaseClient", mock.DatabaseClient)
    mock.db_client = MagicMock()
    mock.dto = RelatedSourceByIDDTO(
        resource_id=mock.resource_id,
        data_source_id=mock.data_source_id,
    )
    mock.access_info = MagicMock()
    return mock


def _check_delete_request_source_relation_called(
    mock_DatabaseClient: MagicMock, mock: MagicMock, id_column_value: str
):
    mock_DatabaseClient.delete_request_source_relation.assert_called_once_with(
        mock.db_client, id_column_name="id", id_column_value=id_column_value
    )


def _check_get_user_id_called(mock: MagicMock):
    mock.db_client.get_user_id.assert_called_once_with(
        email=mock.access_info.user_email
    )


def _check_user_is_creator_of_data_request_called(mock: MagicMock):
    mock.db_client.user_is_creator_of_data_request.assert_called_once_with(
        user_id=mock.user_id, data_request_id=mock.resource_id
    )


def _check_select_from_relation_called(mock: MagicMock):
    mock.db_client._select_from_relation.assert_called_once_with(
        relation_name=Relations.RELATED_SOURCES.value,
        where_mappings={
            "request_id": mock.resource_id,
            "source_id": mock.data_source_id,
        },
        columns=["id"],
    )


def setup_delete_data_request_db_client_mocks(
    mock: MagicMock, user_is_creator: bool = True
):
    mock.db_client._select_from_relation.return_value = [{"id": mock.link_id}]
    mock.db_client.get_user_id.return_value = mock.user_id
    mock.db_client.user_is_creator_of_data_request.return_value = user_is_creator


@patch(f"{PATCH_ROOT}.DatabaseClient")
def test_delete_data_request_related_source_happy_path(
    mock_DatabaseClient,
    data_request_delete_related_source_mocks,
):
    mock = data_request_delete_related_source_mocks
    setup_delete_data_request_db_client_mocks(mock)

    delete_data_request_related_source(
        db_client=mock.db_client,
        access_info=mock.access_info,
        dto=mock.dto,
    )
    _check_common_delete_data_request_calls(mock)
    _check_delete_request_source_relation_called(
        mock_DatabaseClient, mock, id_column_value=mock.link_id
    )
    mock.flask_response_manager.make_response.assert_called_once_with(
        {"message": "Request-Source association deleted."},
        HTTPStatus.OK,
    )


def test_delete_data_request_related_source_user_not_creator(
    data_request_delete_related_source_mocks,
):
    mock = data_request_delete_related_source_mocks
    setup_delete_data_request_db_client_mocks(mock, user_is_creator=False)

    with pytest.raises(FakeAbort):
        delete_data_request_related_source(
            db_client=mock.db_client,
            access_info=mock.access_info,
            dto=mock.dto,
        )
    _check_common_delete_data_request_calls(mock)
    mock.delete_request_source_relation.assert_not_called()
    mock.flask_response_manager.abort.assert_called_once_with(
        message="You do not have permission to delete this Request-Source association.",
        code=HTTPStatus.FORBIDDEN,
    )


def _check_common_delete_data_request_calls(mock: MagicMock):
    _check_select_from_relation_called(mock)
    _check_get_user_id_called(mock)
    _check_user_is_creator_of_data_request_called(mock)


@patch(f"{PATCH_ROOT}.DatabaseClient")
def test_delete_data_request_related_source_user_is_admin(
    mock_DatabaseClient,
    data_request_delete_related_source_mocks,
):
    mock = data_request_delete_related_source_mocks
    setup_delete_data_request_db_client_mocks(mock, user_is_creator=False)

    mock.access_info.permissions = [PermissionsEnum.DB_WRITE]
    delete_data_request_related_source(
        db_client=mock.db_client,
        access_info=mock.access_info,
        dto=mock.dto,
    )
    _check_common_delete_data_request_calls(mock)
    _check_delete_request_source_relation_called(
        mock_DatabaseClient, mock, id_column_value=mock.link_id
    )
    mock.flask_response_manager.make_response.assert_called_once_with(
        {"message": "Request-Source association deleted."},
        HTTPStatus.OK,
    )
