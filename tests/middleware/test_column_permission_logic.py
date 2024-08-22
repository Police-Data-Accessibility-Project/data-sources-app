from unittest.mock import MagicMock

import pytest

from database_client.enums import ColumnPermissionEnum
from middleware.column_permission_logic import (
    get_permitted_columns,
    check_has_permission_to_edit_columns,
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
