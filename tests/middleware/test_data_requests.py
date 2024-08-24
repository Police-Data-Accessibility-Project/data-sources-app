from http import HTTPStatus
from typing import Optional
from unittest.mock import MagicMock, patch, call

import pytest

from database_client.enums import RelationRoleEnum, ColumnPermissionEnum
from database_client.result_formatter import ResultFormatter
from middleware.access_logic import AccessInfo
from middleware.dataclasses import EntryDataRequest
from middleware.enums import AccessTypeEnum, PermissionsEnum
from middleware.data_requests import (
    get_data_requests_relation_role,
    create_data_request_wrapper,
    RELATION,
    get_formatted_data_requests,
    get_standard_and_owner_zipped_data_requests,
    delete_data_request_wrapper,
    delete_data_request,
    check_if_allowed_to_delete_data_request,
    allowed_to_delete_request,
    update_data_request_wrapper,
    get_data_request_by_id_wrapper,
    abort_if_no_results,
    get_data_requestor_with_creator_user_id,
    get_data_requests_wrapper,
    get_zipped_data_requests,
)
from tests.helper_scripts.DynamicMagicMock import DynamicMagicMock
from tests.helper_scripts.common_mocks_and_patches import (
    patch_and_return_mock,
    patch_make_response,
)

PATCH_ROOT = "middleware.data_requests"


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
def mock_get_zipped_data_requests(monkeypatch):
    return patch_and_return_mock(f"{PATCH_ROOT}.get_zipped_data_requests", monkeypatch)


def test_get_data_requestor_with_creator_user_id():
    mock = MagicMock()
    dto = EntryDataRequest(
        entry_data={},
    )
    result = get_data_requestor_with_creator_user_id(
        user_email=mock.user_email, db_client=mock.db_client, dto=dto
    )

    mock.db_client.get_user_id.assert_called_once_with(mock.user_email)
    mock.db_client.create_data_request.assert_called_once_with(
        {
            "creator_user_id": mock.db_client.get_user_id.return_value,
        }
    )
    result = mock.db_client.create_data_request.return_value


@patch(PATCH_ROOT + ".get_formatted_data_requests")
def test_get_data_requests_wrapper(
    mock_get_formatted_data_requests: MagicMock,
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
    mock_make_response.assert_called_once_with(
        {
            "message": "Data requests retrieved",
            "data_requests": mock_get_formatted_data_requests.return_value,
        },
        HTTPStatus.OK,
    )


@patch(PATCH_ROOT + ".make_response")
@patch(PATCH_ROOT + ".get_data_requestor_with_creator_user_id")
def test_create_data_request_wrapper(
    mock_get_data_requestor_with_creator_user_id: MagicMock,
    mock_make_response: MagicMock,
    mock_check_has_permission_to_edit_columns: MagicMock,
):
    mock = MagicMock()
    result = create_data_request_wrapper(
        db_client=mock.db_client, dto=mock.dto, access_info=mock.access_info
    )

    mock_check_has_permission_to_edit_columns.assert_called_once_with(
        db_client=mock.db_client,
        relation=RELATION,
        role=RelationRoleEnum.OWNER,
        columns=list(mock.dto.entry_data.keys()),
    )
    mock_get_data_requestor_with_creator_user_id.assert_called_once_with(
        user_email=mock.access_info.user_email, db_client=mock.db_client, dto=mock.dto
    )
    mock_make_response.assert_called_once_with(
        {
            "message": "Data request created",
            "data_request_id": mock_get_data_requestor_with_creator_user_id.return_value,
        },
        HTTPStatus.OK,
    )


class GetFormattedDataRequestsMocks(DynamicMagicMock):
    get_standard_and_owner_zipped_data_requests: MagicMock
    get_zipped_data_requests: MagicMock


@pytest.fixture
def get_formatted_data_requests_mocks():
    return GetFormattedDataRequestsMocks(
        patch_root=PATCH_ROOT,
    )


@patch.object(ResultFormatter, "convert_data_source_matches")
@patch(PATCH_ROOT + ".get_permitted_columns")
def test_get_zipped_data_requests(
    mock_get_permitted_columns: MagicMock,
    mock_convert_data_source_matches: MagicMock,
):
    mock = MagicMock()
    mock_convert_data_source_matches.return_value = [mock.zipped_data_request]

    results = get_zipped_data_requests(
        db_client=mock.db_client,
        relation_role=mock.relation_role,
        where_mappings=mock.where_mappings,
        not_where_mappings=mock.not_where_mappings,
    )

    mock_convert_data_source_matches.assert_called_once_with(
        data_source_output_columns=mock_get_permitted_columns.return_value,
        results=mock.db_client.get_data_requests.return_value,
    )

    assert results == [mock.zipped_data_request]


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
        not_where_mappings=mock.not_where_mappings,
    )



def test_get_formatted_data_requests_admin(get_formatted_data_requests_mocks):
    mock = get_formatted_data_requests_mocks

    get_formatted_data_requests(
        db_client=mock.db_client,
        access_info=mock.access_info,
        relation_role=RelationRoleEnum.ADMIN,
    )
    mock.get_zipped_data_requests.assert_called_once_with(
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
    mock.get_zipped_data_requests.assert_not_called()
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
    mock.get_zipped_data_requests.assert_not_called()
    mock.get_standard_and_owner_zipped_data_requests.assert_not_called()


def test_get_standard_and_owner_zipped_data_requests(
    mock_get_zipped_data_requests: MagicMock,
):
    mock = MagicMock()
    mock_get_zipped_data_requests.side_effect = [
        [mock.data_request_standard],
        [mock.data_request_owner],
    ]
    mock.db_client.get_user_id.return_value = mock.user_id
    zipped_data_requests = get_standard_and_owner_zipped_data_requests(
        user_email=mock.user_email, db_client=mock.db_client
    )
    assert zipped_data_requests == [mock.data_request_owner, mock.data_request_standard]
    expected_mapping = {"creator_user_id": mock.user_id}
    mock_get_zipped_data_requests.assert_has_calls(
        [
            call(
                db_client=mock.db_client,
                relation_role=RelationRoleEnum.STANDARD,
                not_where_mappings=expected_mapping,
            ),
            call(
                db_client=mock.db_client,
                relation_role=RelationRoleEnum.OWNER,
                where_mappings=expected_mapping,
            ),
        ],
        any_order=True,
    )


@patch(PATCH_ROOT + ".check_if_allowed_to_delete_data_request")
@patch(PATCH_ROOT + ".delete_data_request")
def test_delete_data_request_wrapper(
    mock_delete_data_request: MagicMock,
    mock_check_if_allowed_to_delete_data_request: MagicMock,
):
    mock = MagicMock()
    result = delete_data_request_wrapper(
        db_client=mock.db_client,
        data_request_id=mock.data_request_id,
        access_info=mock.access_info,
    )
    mock_check_if_allowed_to_delete_data_request.assert_called_once_with(
        mock.access_info, mock.data_request_id, mock.db_client
    )
    mock_delete_data_request.assert_called_once_with(
        mock.data_request_id, mock.db_client
    )
    assert result == mock_delete_data_request.return_value


@patch(PATCH_ROOT + ".message_response")
def test_delete_data_request(
    mock_message_response: MagicMock,
):
    mock = MagicMock()
    result = delete_data_request(mock.data_request_id, mock.db_client)
    mock.db_client.delete_data_request.assert_called_once_with(mock.data_request_id)
    mock_message_response.assert_called_once_with("Data request deleted", HTTPStatus.OK)
    assert result == mock_message_response.return_value


@pytest.fixture
def mock_abort(monkeypatch):
    return patch_and_return_mock(f"{PATCH_ROOT}.abort", monkeypatch)


@pytest.fixture
def mock_make_response(monkeypatch):
    return patch_and_return_mock(f"{PATCH_ROOT}.make_response", monkeypatch)


@pytest.mark.parametrize(
    "allowed_to_delete_request, abort_called",
    [(True, False), (False, True)],
)
@patch(PATCH_ROOT + ".allowed_to_delete_request")
def test_check_if_allowed_to_delete_data_request(
    mock_allowed_to_delete_request: MagicMock,
    allowed_to_delete_request,
    abort_called,
    mock_abort: MagicMock,
):
    mock = MagicMock()
    mock_allowed_to_delete_request.return_value = allowed_to_delete_request
    check_if_allowed_to_delete_data_request(
        access_info=mock.access_info,
        data_request_id=mock.data_request_id,
        db_client=mock.db_client,
    )
    mock_allowed_to_delete_request.assert_called_once_with(
        mock.access_info, mock.data_request_id, mock.db_client
    )
    if abort_called:
        mock_abort.assert_called_once_with(
            code=HTTPStatus.FORBIDDEN,
            message="You do not have permission to delete this data request",
        )
    else:
        mock_abort.assert_not_called()


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


def test_update_data_request_wrapper(
    mock_get_data_requests_relation_role,
    mock_check_has_permission_to_edit_columns,
    mock_message_response,
):
    mock = MagicMock()
    result = update_data_request_wrapper(
        db_client=mock.db_client,
        dto=mock.dto,
        data_request_id=mock.data_request_id,
        access_info=mock.access_info,
    )
    mock_get_data_requests_relation_role.assert_called_once_with(
        mock.db_client,
        mock.data_request_id,
        mock.access_info,
    )
    mock_check_has_permission_to_edit_columns.assert_called_once_with(
        db_client=mock.db_client,
        relation=RELATION,
        role=mock_get_data_requests_relation_role.return_value,
        columns=list(mock.dto.entry_data.keys()),
    )
    mock_message_response.assert_called_once_with("Data request updated", HTTPStatus.OK)
    assert result == mock_message_response.return_value


def test_get_data_request_by_id_wrapper(
    mock_get_zipped_data_requests,
    mock_get_data_requests_relation_role,
    mock_make_response,
    monkeypatch,
):
    mock = MagicMock()
    monkeypatch.setattr(
        f"{PATCH_ROOT}.abort_if_no_results",
        mock.abort_if_no_results,
    )

    result = get_data_request_by_id_wrapper(
        db_client=mock.db_client,
        access_info=mock.access_info,
        data_request_id=mock.data_request_id,
    )
    mock_get_data_requests_relation_role.assert_called_once_with(
        mock.db_client,
        data_request_id=mock.data_request_id,
        access_info=mock.access_info,
    )
    mock_get_zipped_data_requests.assert_called_once_with(
        db_client=mock.db_client,
        relation_role=mock_get_data_requests_relation_role.return_value,
        where_mappings={"id": mock.data_request_id},
    )
    mock.abort_if_no_results.assert_called_once_with(
        mock_get_zipped_data_requests.return_value
    )
    mock_make_response.assert_called_once_with(
        {
            "message": "Data request retrieved",
            "data_request": mock_get_zipped_data_requests.return_value[0],
        },
        HTTPStatus.OK,
    )
    assert result == mock_make_response.return_value


def test_if_no_results_happy_path(mock_abort):
    abort_if_no_results([1, 2, 3])
    mock_abort.assert_not_called()


def test_if_no_results_abort_called(mock_abort):
    abort_if_no_results([])
    mock_abort.assert_called_once_with(
        code=HTTPStatus.OK,
        message="Data request not found",
    )
