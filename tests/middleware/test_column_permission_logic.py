from typing import List
from unittest.mock import MagicMock, patch

import pytest

from database_client.enums import ColumnPermissionEnum, RelationRoleEnum
from middleware.access_logic import AccessInfo
from middleware.column_permission_logic import (
    get_permitted_columns,
    check_has_permission_to_edit_columns,
    create_column_permissions_string_table,
    get_relation_role,
    RelationRoleParameters,
)
from middleware.custom_dataclasses import DeferredFunction
from middleware.enums import PermissionsEnum, AccessTypeEnum


def test_get_permitted_columns():
    mock = MagicMock()

    get_permitted_columns(
        db_client=mock.db_client,
        relation=mock.relation,
        role=mock.role,
        column_permission=mock.column_permission,
    )

    mock.db_client.get_permitted_columns.assert_called_once_with(
        relation=mock.relation, role=mock.role, column_permission=mock.column_permission
    )


@pytest.fixture
def mock_abort(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr("middleware.flask_response_manager.abort", mock)
    return mock


def test_check_has_permission_to_edit_columns_success(mock_abort):
    mock = MagicMock()
    mock.db_client.get_permitted_columns.return_value = ["column_a", "column_b"]

    check_has_permission_to_edit_columns(
        db_client=mock.db_client,
        relation=mock.relation,
        role=mock.role,
        columns=["column_a", "column_b"],
    )

    mock_abort.assert_not_called()

    mock.db_client.get_permitted_columns.assert_called_once_with(
        relation=mock.relation,
        role=mock.role,
        column_permission=ColumnPermissionEnum.WRITE,
    )


def test_check_has_permission_to_edit_columns_fail(mock_abort):
    mock = MagicMock()
    mock.db_client.get_permitted_columns.return_value = ["column_a"]

    check_has_permission_to_edit_columns(
        db_client=mock.db_client,
        relation=mock.relation,
        role=mock.role,
        columns=["column_a", "column_b"],
    )

    mock.db_client.get_permitted_columns.assert_called_once_with(
        relation=mock.relation,
        role=mock.role,
        column_permission=ColumnPermissionEnum.WRITE,
    )

    mock_abort.assert_called_once()


@patch("middleware.column_permission_logic.DatabaseClient")
def test_create_column_permissions_string_table(mock_DatabaseClient: MagicMock):
    mock_db_client = MagicMock()
    mock_DatabaseClient.return_value = mock_db_client
    mock_db_client.get_column_permissions_as_permission_table.return_value = [
        {
            "associated_column": "column_a",
            "STANDARD": "READ",
            "OWNER": "READ",
            "ADMIN": "WRITE",
        },
        {
            "associated_column": "column_b",
            "STANDARD": "READ",
            "OWNER": "WRITE",
            "ADMIN": "WRITE",
        },
        {
            "associated_column": "column_c",
            "STANDARD": "NONE",
            "OWNER": "NONE",
            "ADMIN": "READ",
        },
    ]

    result = create_column_permissions_string_table(relation="test_relation")

    mock_db_client.get_column_permissions_as_permission_table.assert_called_once_with(
        relation="test_relation",
    )

    assert (
        result.replace(" ", "").replace("-", "").replace("\n", "")
        == """
    | associated_column | STANDARD | OWNER | ADMIN |
    |-------------------|----------|-------|-------|
    | column_a          | READ     | READ  | WRITE |
    | column_b          | READ     | WRITE | WRITE |
    | column_c          | NONE     | NONE  | READ  |
    """.replace(
            " ", ""
        )
        .replace("-", "")
        .replace("\n", "")
    )


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
            AccessInfo(
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
            access_info=AccessInfo(
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
