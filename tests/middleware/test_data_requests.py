from unittest.mock import MagicMock, patch

import pytest

from database_client.enums import RelationRoleEnum
from middleware.access_logic import AccessInfo
from middleware.enums import AccessTypeEnum, PermissionsEnum
from middleware.data_requests import get_data_requests_relation_role, create_data_request_wrapper, RELATION

PATCH_ROOT = "middleware.data_requests."

@pytest.mark.parametrize(
    "access_type, is_owner, permissions, expected_relation_role",
    (
        (AccessTypeEnum.API_KEY, False, [], RelationRoleEnum.STANDARD),
        (AccessTypeEnum.JWT, False, [], RelationRoleEnum.STANDARD),
        (AccessTypeEnum.JWT, False, [PermissionsEnum.DB_WRITE], RelationRoleEnum.ADMIN),
        (AccessTypeEnum.JWT, True, [], RelationRoleEnum.OWNER),
        (
            AccessTypeEnum.JWT,
            False,
            [PermissionsEnum.READ_ALL_USER_INFO],
            RelationRoleEnum.STANDARD,
        ),
    ),
)
def test_get_data_requests_relation_role(
    access_type: AccessTypeEnum,
    is_owner: bool,
    permissions: list[PermissionsEnum],
    expected_relation_role: RelationRoleEnum,
):
    mock = MagicMock()
    mock.db_client.user_is_creator_of_data_request.return_value = is_owner
    relation_role = get_data_requests_relation_role(
        db_client=mock.db_client,
        data_request_id=mock.data_request_id,
        access_info=AccessInfo(
            user_email="test_user", access_type=access_type, permissions=permissions
        ),
    )
    assert relation_role == expected_relation_role

@patch(PATCH_ROOT + "check_has_permission_to_edit_columns")
@patch(PATCH_ROOT + "get_data_requestor_with_creator_user_id")
@patch(PATCH_ROOT + "make_response")
def test_create_data_request_wrapper(
    mock_check_has_permission_to_edit_columns: MagicMock,
    mock_get_data_requestor_with_creator_user_id: MagicMock,
    mock_make_response: MagicMock,
):
    mock = MagicMock()
    result = create_data_request_wrapper(
        db_client=mock.db_client,
        dto=mock.dto,
        access_info=mock.access_info
    )

    mock_check_has_permission_to_edit_columns.assert_called_once_with(
        db_client=mock.db_client,
        relation=RELATION,
        role=RelationRoleEnum.OWNER,
        columns=list(mock.dto.entry_data.keys())
    )
    # mock_get_data_requestor_with_creator_user_id.assert_called_once_with(
    #     user_email=mock.access_info.user_email,
    #     db_client=mock.db_client,
    #     dto=mock.dto
    # )
    # mock_make_response.assert_called_once_with(
    #     mock_get_data_requestor_with_creator_user_id.return_value,
    #     mock_check_has_permission_to_edit_columns.return_value
    # )
    # assert result
