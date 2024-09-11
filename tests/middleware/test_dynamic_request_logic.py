from http import HTTPStatus
from unittest.mock import MagicMock

import pytest

from database_client.database_client import DatabaseClient
from database_client.db_client_dataclasses import WhereMapping
from database_client.enums import ColumnPermissionEnum
from middleware.dynamic_request_logic import (
    results_dependent_response,
    get_by_id,
    get_many,
    post_entry,
    put_entry,
    check_for_delete_permissions,
    delete_entry,
    check_requested_columns,
    optionally_limit_to_requested_columns,
)
from middleware.schema_and_dto_logic.response_schemas import EntryDataResponseSchema
from middleware.util_dynamic import call_if_not_none, execute_if_not_none
from tests.fixtures import mock_flask_response_manager
from tests.helper_scripts.common_mocks_and_patches import patch_and_return_mock

PATCH_ROOT = "middleware.dynamic_request_logic"


@pytest.fixture
def mock_message_response(monkeypatch):
    return patch_and_return_mock(f"{PATCH_ROOT}.message_response", monkeypatch)


@pytest.fixture
def mock_get_permitted_columns(monkeypatch):
    return patch_and_return_mock(f"{PATCH_ROOT}.get_permitted_columns", monkeypatch)


@pytest.fixture
def mock_check_has_permission_to_edit_columns(monkeypatch):
    return patch_and_return_mock(
        f"{PATCH_ROOT}.check_has_permission_to_edit_columns", monkeypatch
    )


@pytest.fixture
def mock_abort(monkeypatch):
    return patch_and_return_mock(
        f"middleware.flask_response_manager.abort", monkeypatch
    )


def test_results_dependent_response_with_results(mock_message_response):

    results_dependent_response(
        entry_name="test entry",
        results=[{"test": 1}],
    )

    mock_message_response.assert_called_once_with(
        message="test entry found", data={"test": 1}, validation_schema=EntryDataResponseSchema
    )


def test_results_dependent_response_with_no_results(mock_message_response):

    results_dependent_response(
        entry_name="test entry",
        results=[],
    )

    mock_message_response.assert_called_once_with(
        message="test entry not found",
    )


def test_get_by_id(monkeypatch, mock_get_permitted_columns):
    mock = MagicMock()
    monkeypatch.setattr(
        f"{PATCH_ROOT}.results_dependent_response", mock.results_dependent_response
    )
    result = get_by_id(
        middleware_parameters=mock.mp,
        id=mock.id,
        id_column_name=mock.id_column_name,
        relation_role_parameters=mock.relation_role_parameters,
    )

    mock.relation_role_parameters.get_relation_role_from_parameters.assert_called_once_with(
        access_info=mock.mp.access_info
    )

    mock_get_permitted_columns.assert_called_once_with(
        db_client=mock.mp.db_client,
        relation=mock.mp.relation,
        role=mock.relation_role_parameters.get_relation_role_from_parameters.return_value,
        column_permission=ColumnPermissionEnum.READ,
    )

    mock.mp.db_client_method.assert_called_once_with(
        mock.mp.db_client,
        relation=mock.mp.relation,
        columns=mock_get_permitted_columns.return_value,
        where_mappings=[
            WhereMapping(column=mock.id_column_name, value=mock.id)
        ],
    )

    mock.results_dependent_response.assert_called_once_with(
        mock.mp.entry_name, mock.mp.db_client_method.return_value
    )

    assert result == mock.results_dependent_response.return_value


def test_get_many(monkeypatch, mock_get_permitted_columns):
    mock = MagicMock()
    monkeypatch.setattr(
        f"{PATCH_ROOT}.multiple_results_response", mock.multiple_results_response
    )
    monkeypatch.setattr(
        f"{PATCH_ROOT}.optionally_limit_to_requested_columns",
        mock.optionally_limit_to_requested_columns,
    )
    result = get_many(
        middleware_parameters=mock.mp,
        page=mock.page,
        relation_role_parameters=mock.relation_role_parameters,
        requested_columns=mock.requested_columns,
    )

    mock.relation_role_parameters.get_relation_role_from_parameters.assert_called_once_with(
        access_info=mock.mp.access_info
    )

    mock_get_permitted_columns.assert_called_once_with(
        db_client=mock.mp.db_client,
        relation=mock.mp.relation,
        role=mock.relation_role_parameters.get_relation_role_from_parameters.return_value,
        column_permission=ColumnPermissionEnum.READ,
    )

    mock.optionally_limit_to_requested_columns.assert_called_once_with(
        mock_get_permitted_columns.return_value, mock.requested_columns
    )

    mock.mp.db_client_method.assert_called_once_with(
        mock.mp.db_client,
        relation=mock.mp.relation,
        columns=mock.optionally_limit_to_requested_columns.return_value,
        page=mock.page,
    )

    mock.multiple_results_response.assert_called_once_with(
        message=f"{mock.mp.entry_name} found",
        data=mock.mp.db_client_method.return_value,
    )

    assert result == mock.multiple_results_response.return_value


@pytest.fixture
def mock_check_requested_columns(monkeypatch) -> MagicMock:
    mock = MagicMock()
    monkeypatch.setattr(f"{PATCH_ROOT}.check_requested_columns", mock)
    return mock


def test_optionally_limit_to_requested_columns_with_no_requested_columns(
    mock_check_requested_columns,
):
    mock = MagicMock()
    assert mock.permitted_columns == optionally_limit_to_requested_columns(
        permitted_columns=mock.permitted_columns,
        requested_columns=None,
    )
    mock_check_requested_columns.assert_not_called()

def test_optionally_limit_to_requested_columns_with_requested_columns(
    mock_check_requested_columns,
):
    mock = MagicMock()
    assert mock.requested_columns == optionally_limit_to_requested_columns(
        permitted_columns=mock.permitted_columns,
        requested_columns=mock.requested_columns,
    )
    mock_check_requested_columns.assert_called_once_with(
        mock.requested_columns, mock.permitted_columns
    )


def test_execute_if_none_is_none():
    # Nothing should happen, both if None is provided, and if None is not provided (because the default is None)
    execute_if_not_none(None)
    execute_if_not_none()


def test_execute_if_none_is_not_none():
    mock = MagicMock()
    execute_if_not_none(mock)
    mock.execute.assert_called_once()


def test_post_entry(monkeypatch, mock_check_has_permission_to_edit_columns):
    mock = MagicMock()
    monkeypatch.setattr(f"{PATCH_ROOT}.execute_if_not_none", mock.execute_if_not_none)
    monkeypatch.setattr(f"{PATCH_ROOT}.created_id_response", mock.created_id_response)

    result = post_entry(
        middleware_parameters=mock.mp,
        entry=mock.entry,
        pre_insertion_function_with_parameters=mock.pre_insertion_function_with_parameters,
        relation_role_parameters=mock.relation_role_parameters,
    )

    mock.relation_role_parameters.get_relation_role_from_parameters.assert_called_once_with(
        access_info=mock.mp.access_info
    )

    mock_check_has_permission_to_edit_columns.assert_called_once_with(
        db_client=mock.mp.db_client,
        relation=mock.mp.relation,
        role=mock.relation_role_parameters.get_relation_role_from_parameters.return_value,
        columns=list(mock.entry.keys()),
    )

    mock.execute_if_not_none.assert_called_once_with(
        mock.pre_insertion_function_with_parameters
    )

    mock.mp.db_client_method.assert_called_once_with(
        mock.mp.db_client, column_value_mappings=mock.entry
    )

    mock.created_id_response.assert_called_once_with(
        new_id=str(mock.mp.db_client_method.return_value),
        message=f"{mock.mp.entry_name} created.",
    )

    assert result == mock.created_id_response.return_value


def test_put_entry(
    monkeypatch, mock_check_has_permission_to_edit_columns, mock_message_response
):
    mock = MagicMock()

    result = put_entry(
        middleware_parameters=mock.mp,
        entry=mock.entry,
        entry_id=mock.entry_id,
        relation_role_parameters=mock.relation_role_parameters,
    )

    mock.relation_role_parameters.get_relation_role_from_parameters.assert_called_once_with(
        access_info=mock.mp.access_info
    )

    mock_check_has_permission_to_edit_columns.assert_called_once_with(
        db_client=mock.mp.db_client,
        relation=mock.mp.relation,
        role=mock.relation_role_parameters.get_relation_role_from_parameters.return_value,
        columns=list(mock.entry.keys()),
    )

    mock.mp.db_client_method.assert_called_once_with(
        mock.mp.db_client, column_edit_mappings=mock.entry, entry_id=mock.entry_id
    )

    mock_message_response.assert_called_once_with(
        message=f"{mock.mp.entry_name} updated."
    )

    assert result == mock_message_response.return_value


def test_check_for_delete_permission_check_function_returns_true(mock_abort):
    mock_check_function = MagicMock()
    mock_check_function.execute.return_value = True
    check_for_delete_permissions(
        check_function=mock_check_function, entry_name="test entry"
    )
    mock_abort.assert_not_called()


def test_check_for_delete_permission_check_function_returns_false(mock_abort):
    mock_check_function = MagicMock()
    mock_check_function.execute.return_value = False
    check_for_delete_permissions(
        check_function=mock_check_function, entry_name="test entry"
    )
    mock_abort.assert_called_once_with(
        code=HTTPStatus.FORBIDDEN,
        message="You do not have permission to delete this test entry.",
    )


def test_call_if_not_none_is_none():
    mock_func = MagicMock()
    call_if_not_none(None, mock_func)

    assert not mock_func.called


def test_call_if_not_none_is_not_none():
    mock_func = MagicMock()
    call_if_not_none(1, mock_func, a=1)

    mock_func.assert_called_once_with(a=1)


def test_delete_entry(monkeypatch, mock_message_response):
    mock = MagicMock()

    monkeypatch.setattr(f"{PATCH_ROOT}.call_if_not_none", mock.call_if_not_none)

    result = delete_entry(
        middleware_parameters=mock.mp,
        entry_id=mock.entry_id,
        id_column_name=mock.id_column_name,
        permission_checking_function=mock.permission_checking_function,
    )

    mock.call_if_not_none.assert_called_once_with(
        obj=mock.permission_checking_function,
        func=check_for_delete_permissions,
        check_function=mock.permission_checking_function,
        entry_name=mock.mp.entry_name,
    )

    mock.mp.db_client_method.assert_called_once_with(
        mock.mp.db_client,
        id_column_name=mock.id_column_name,
        id_column_value=mock.entry_id,
    )

    mock_message_response.assert_called_once_with(f"{mock.mp.entry_name} deleted.")

    assert result == mock_message_response.return_value


def test_check_requested_columns_happy_path(mock_flask_response_manager, monkeypatch):
    mock = MagicMock()
    mock.get_invalid_columns.return_value = []
    monkeypatch.setattr(f"{PATCH_ROOT}.get_invalid_columns", mock.get_invalid_columns)
    check_requested_columns(
        requested_columns=mock.requested_columns,
        permitted_columns=mock.permitted_columns,
    )

    mock.get_invalid_columns.assert_called_once_with(
        mock.requested_columns, mock.permitted_columns
    )
    mock_flask_response_manager.abort.assert_not_called()


def test_check_requested_columns_invalid_columns(
    mock_flask_response_manager, monkeypatch
):
    mock = MagicMock()
    mock.get_invalid_columns.return_value = ["invalid_column"]
    monkeypatch.setattr(f"{PATCH_ROOT}.get_invalid_columns", mock.get_invalid_columns)
    check_requested_columns(
        requested_columns=mock.requested_columns,
        permitted_columns=mock.permitted_columns,
    )

    mock.get_invalid_columns.assert_called_once_with(
        mock.requested_columns, mock.permitted_columns
    )
    mock_flask_response_manager.abort.assert_called_once_with(
        code=HTTPStatus.FORBIDDEN,
        message=f"The following columns are either invalid or not permitted for your access permissions: {mock.get_invalid_columns.return_value}",
    )
