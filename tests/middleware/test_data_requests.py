from unittest.mock import MagicMock

import pytest

from database_client.enums import RelationRoleEnum
from middleware.access_logic import AccessInfo
from middleware.enums import AccessTypeEnum, PermissionsEnum
from middleware.data_requests import get_data_requests_relation_role


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
