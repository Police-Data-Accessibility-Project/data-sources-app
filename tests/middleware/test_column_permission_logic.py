from typing import List
from unittest.mock import MagicMock, patch

import pytest

from db.enums import ColumnPermissionEnum, RelationRoleEnum
from middleware.access_logic import AccessInfoPrimary
from middleware.column_permission_logic import (
    get_permitted_columns,
    check_has_permission_to_edit_columns,
    create_column_permissions_string_table,
    get_relation_role,
    RelationRoleParameters,
)
from middleware.custom_dataclasses import DeferredFunction
from middleware.enums import PermissionsEnum, AccessTypeEnum


@pytest.mark.parametrize(
    "access_type, permissions, expected_result",
    (
        (AccessTypeEnum.API_KEY, [], RelationRoleEnum.STANDARD),
        (AccessTypeEnum.API_KEY, [PermissionsEnum.DB_WRITE], RelationRoleEnum.STANDARD),
        (AccessTypeEnum.JWT, [], RelationRoleEnum.STANDARD),
        (AccessTypeEnum.JWT, [PermissionsEnum.DB_WRITE], RelationRoleEnum.ADMIN),
    ),
)
def test_get_relation_role(
    access_type: AccessTypeEnum,
    permissions: List[PermissionsEnum],
    expected_result: RelationRoleEnum,
):
    assert (
        get_relation_role(
            AccessInfoPrimary(
                access_type=access_type,
                permissions=permissions,
                user_email="test_user",
            )
        )
        == expected_result
    )


@pytest.fixture
def mock_relation_role_function_with_params(monkeypatch):
    mock = MagicMock(spec=DeferredFunction)
    monkeypatch.setattr("middleware.column_permission_logic.get_relation_role", mock)
    return mock


def test_get_relation_role_parameters_override(
    mock_relation_role_function_with_params: MagicMock,
):
    rrp = RelationRoleParameters(
        relation_role_function_with_params=mock_relation_role_function_with_params,
        relation_role_override=RelationRoleEnum.ADMIN,
    )

    assert (
        rrp.get_relation_role_from_parameters(
            access_info=AccessInfoPrimary(
                access_type=AccessTypeEnum.API_KEY,
                user_email="test_user",
            )
        )
        == RelationRoleEnum.ADMIN
    )


def test_get_relation_role_parameters_no_override(
    mock_relation_role_function_with_params: MagicMock,
):
    rrp = RelationRoleParameters(
        relation_role_function_with_params=mock_relation_role_function_with_params,
    )

    mock_access_info = MagicMock()
    rrp.get_relation_role_from_parameters(access_info=mock_access_info)

    mock_relation_role_function_with_params.execute.assert_called_with(
        access_info=mock_access_info
    )
