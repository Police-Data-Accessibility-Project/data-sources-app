from unittest.mock import MagicMock, patch

import pytest

from database_client.enums import ColumnPermissionEnum
from middleware.column_permission_logic import (
    get_permitted_columns,
    check_has_permission_to_edit_columns,
    create_column_permissions_string_table,
)


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
    monkeypatch.setattr("middleware.column_permission_logic.abort", mock)
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
    """.replace(" ", "").replace("-", "").replace("\n", "")
    )
