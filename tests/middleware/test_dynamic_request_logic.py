from http import HTTPStatus
from unittest.mock import MagicMock

import pytest

from database_client.database_client import DatabaseClient
from database_client.db_client_dataclasses import WhereMapping
from database_client.enums import ColumnPermissionEnum
from middleware.dynamic_request_logic.common_functions import check_for_id
from middleware.dynamic_request_logic.delete_logic import (
    check_for_delete_permissions,
    delete_entry,
)
from middleware.dynamic_request_logic.get_by_id_logic import (
    results_dependent_response,
    get_by_id,
)
from middleware.dynamic_request_logic.get_many_logic import (
    get_many,
    optionally_limit_to_requested_columns,
    check_requested_columns,
)
from middleware.dynamic_request_logic.post_logic import post_entry
from middleware.dynamic_request_logic.put_logic import put_entry
from middleware.dynamic_request_logic.supporting_classes import IDInfo
from middleware.primary_resource_logic.data_requests import RelatedSourceByIDDTO

from middleware.schema_and_dto_logic.response_schemas import EntryDataResponseSchema
from middleware.util_dynamic import call_if_not_none, execute_if_not_none
from tests.fixtures import mock_flask_response_manager, FakeAbort
from tests.helper_scripts.common_mocks_and_patches import (
    patch_and_return_mock,
    multi_monkeypatch,
)

PATCH_ROOT = "middleware.dynamic_request_logic"


@pytest.fixture
def mock_message_response(monkeypatch):
    return patch_and_return_mock(f"{PATCH_ROOT}.message_response", monkeypatch)


@pytest.fixture
def mock_get_permitted_columns(monkeypatch):
    return patch_and_return_mock(f"{PATCH_ROOT}.get_permitted_columns", monkeypatch)


@pytest.fixture
def mock_abort(monkeypatch):
    return patch_and_return_mock(
        f"middleware.flask_response_manager.abort", monkeypatch
    )


def test_results_dependent_response_with_results(monkeypatch):
    mock_message_response = patch_and_return_mock(
        f"{PATCH_ROOT}.get_by_id_logic.message_response", monkeypatch
    )

    results_dependent_response(
        entry_name="test entry",
        results=[{"test": 1}],
    )

    mock_message_response.assert_called_once_with(
        message="test entry found", data={"test": 1}, validation_schema=EntryDataResponseSchema
    )


def test_results_dependent_response_with_no_results(monkeypatch):
    mock_message_response = patch_and_return_mock(
        f"{PATCH_ROOT}.get_by_id_logic.message_response", monkeypatch
    )

    results_dependent_response(
        entry_name="test entry",
        results=[],
    )

    mock_message_response.assert_called_once_with(
        message="test entry not found",
    )


def test_get_by_id(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr(
        f"{PATCH_ROOT}.get_by_id_logic.results_dependent_response",
        mock.results_dependent_response,
    )
    monkeypatch.setattr(
        f"{PATCH_ROOT}.get_by_id_logic.get_permitted_columns",
        mock.get_permitted_columns,
    )
    monkeypatch.setattr(f"{PATCH_ROOT}.get_by_id_logic.check_for_id", mock.check_for_id)
    id_info = IDInfo(id_column_value=mock.id, id_column_name=mock.id_column_name)
    monkeypatch.setattr(
        f"{PATCH_ROOT}.get_by_id_logic.IDInfo", MagicMock(return_value=id_info)
    )
    result = get_by_id(
        middleware_parameters=mock.mp,
        id=mock.id,
        id_column_name=mock.id_column_name,
        relation_role_parameters=mock.relation_role_parameters,
    )

    mock.check_for_id.assert_called_once_with(
        db_client=mock.mp.db_client, table_name=mock.mp.relation, id_info=id_info
    )

    mock.relation_role_parameters.get_relation_role_from_parameters.assert_called_once_with(
        access_info=mock.mp.access_info
    )

    mock.get_permitted_columns.assert_called_once_with(
        db_client=mock.mp.db_client,
        relation=mock.mp.relation,
        role=mock.relation_role_parameters.get_relation_role_from_parameters.return_value,
        column_permission=ColumnPermissionEnum.READ,
    )

    mock.mp.db_client_method.assert_called_once_with(
        mock.mp.db_client,
        relation=mock.mp.relation,
        columns=mock.get_permitted_columns.return_value,
        where_mappings=[
            WhereMapping(column=mock.id_column_name, value=mock.id)
        ],
    )

    mock.results_dependent_response.assert_called_once_with(
        mock.mp.entry_name, mock.mp.db_client_method.return_value
    )

    assert result == mock.results_dependent_response.return_value


def test_get_many(monkeypatch):
    mock = MagicMock()
    multi_monkeypatch(
        monkeypatch,
        patch_root=f"{PATCH_ROOT}.get_many_logic",
        mock=mock,
        functions_to_patch=[
            "get_permitted_columns",
            "optionally_limit_to_requested_columns",
            "multiple_results_response",
        ],
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

    mock.get_permitted_columns.assert_called_once_with(
        db_client=mock.mp.db_client,
        relation=mock.mp.relation,
        role=mock.relation_role_parameters.get_relation_role_from_parameters.return_value,
        column_permission=ColumnPermissionEnum.READ,
    )

    mock.optionally_limit_to_requested_columns.assert_called_once_with(
        mock.get_permitted_columns.return_value, mock.requested_columns
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
    monkeypatch.setattr(f"{PATCH_ROOT}.get_many_logic.check_requested_columns", mock)
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


def test_post_entry(monkeypatch):
    mock = MagicMock()
    multi_monkeypatch(
        monkeypatch,
        patch_root=f"{PATCH_ROOT}.post_logic",
        mock=mock,
        functions_to_patch=[
            "execute_if_not_none",
            "created_id_response",
        ],
    )
    monkeypatch.setattr(
        f"{PATCH_ROOT}.supporting_classes.check_has_permission_to_edit_columns",
        mock.check_has_permission_to_edit_columns,
    )
    result = post_entry(
        middleware_parameters=mock.mp,
        entry=mock.entry,
        pre_insertion_function_with_parameters=mock.pre_insertion_function_with_parameters,
        relation_role_parameters=mock.relation_role_parameters,
    )

    mock.relation_role_parameters.get_relation_role_from_parameters.assert_called_once_with(
        access_info=mock.mp.access_info
    )

    mock.check_has_permission_to_edit_columns.assert_called_once_with(
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


def test_put_entry(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr(
        f"{PATCH_ROOT}.put_logic.message_response",
        mock.message_response,
    )
    monkeypatch.setattr(
        f"{PATCH_ROOT}.supporting_classes.check_has_permission_to_edit_columns",
        mock.check_has_permission_to_edit_columns,
    )

    result = put_entry(
        middleware_parameters=mock.mp,
        entry=mock.entry,
        entry_id=mock.entry_id,
        relation_role_parameters=mock.relation_role_parameters,
    )

    mock.relation_role_parameters.get_relation_role_from_parameters.assert_called_once_with(
        access_info=mock.mp.access_info
    )

    mock.check_has_permission_to_edit_columns.assert_called_once_with(
        db_client=mock.mp.db_client,
        relation=mock.mp.relation,
        role=mock.relation_role_parameters.get_relation_role_from_parameters.return_value,
        columns=list(mock.entry.keys()),
    )

    mock.mp.db_client_method.assert_called_once_with(
        mock.mp.db_client, column_edit_mappings=mock.entry, entry_id=mock.entry_id
    )

    mock.message_response.assert_called_once_with(
        message=f"{mock.mp.entry_name} updated."
    )

    assert result == mock.message_response.return_value


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


def test_delete_entry(monkeypatch):
    mock = MagicMock()
    multi_monkeypatch(
        monkeypatch,
        patch_root=f"{PATCH_ROOT}.delete_logic",
        mock=mock,
        functions_to_patch=[
            "check_for_id",
            "call_if_not_none",
            "message_response",
        ],
    )

    result = delete_entry(
        middleware_parameters=mock.mp,
        id_info=mock.id_info,
        permission_checking_function=mock.permission_checking_function,
    )

    mock.check_for_id.assert_called_once_with(
        table_name=mock.mp.relation,
        id_info=mock.id_info,
        db_client=mock.mp.db_client,
    )

    mock.call_if_not_none.assert_called_once_with(
        obj=mock.permission_checking_function,
        func=check_for_delete_permissions,
        check_function=mock.permission_checking_function,
        entry_name=mock.mp.entry_name,
    )

    mock.mp.db_client_method.assert_called_once_with(
        mock.mp.db_client,
        id_column_name=mock.id_info.id_column_name,
        id_column_value=mock.check_for_id.return_value,
    )

    mock.message_response.assert_called_once_with(f"{mock.mp.entry_name} deleted.")

    assert result == mock.message_response.return_value


def test_delete_id_not_found(monkeypatch, mock_flask_response_manager):
    mock = MagicMock()
    mock.flask_response_manager = mock_flask_response_manager
    monkeypatch.setattr(mock, f"{PATCH_ROOT}.DatabaseClient", mock.DatabaseClient)
    mock.dto = RelatedSourceByIDDTO(
        resource_id=mock.resource_id,
        data_source_id=mock.data_source_id,
    )
    mock.access_info = MagicMock()
    mock.db_client._select_from_single_relation.return_value = []
    with pytest.raises(FakeAbort):
        delete_entry(
            middleware_parameters=mock.mp,
            id_info=mock.id_info,
            permission_checking_function=mock.permission_checking_function,
        )
    mock.mp.db_client._select_from_single_relation.assert_called_once_with(
        relation_name=mock.mp.relation,
        where_mappings=mock.id_info.where_mappings,
        columns=[mock.id_info.id_column_name],
    )
    mock.db_client.get_user_id.assert_not_called()
    mock.user_is_creator_of_data_request.assert_not_called()
    mock.flask_response_manager.abort.assert_called_once_with(
        message=f"Entry for {mock.id_info.where_mappings} not found.",
        code=HTTPStatus.NOT_FOUND,
    )


def test_check_requested_columns_happy_path(mock_flask_response_manager, monkeypatch):
    mock = MagicMock()
    mock.get_invalid_columns.return_value = []
    monkeypatch.setattr(
        f"{PATCH_ROOT}.get_many_logic.get_invalid_columns", mock.get_invalid_columns
    )
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
    monkeypatch.setattr(
        f"{PATCH_ROOT}.get_many_logic.get_invalid_columns", mock.get_invalid_columns
    )
    with pytest.raises(FakeAbort):
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


def test_check_for_id_happy_path(mock_flask_response_manager):
    mock = MagicMock()
    mock.db_client._select_from_single_relation.return_value = [{"id": 1}]
    mock.id_info.id_column_name = "id"

    result = check_for_id(
        table_name=mock.table_name, id_info=mock.id_info, db_client=mock.db_client
    )

    assert result == 1

    mock.db_client._select_from_single_relation.assert_called_once_with(
        relation_name=mock.table_name,
        where_mappings=mock.id_info.where_mappings,
        columns=[mock.id_info.id_column_name],
    )
    mock_flask_response_manager.abort.assert_not_called()


def test_check_for_id_no_id(mock_flask_response_manager):
    mock = MagicMock()
    mock.db_client._select_from_single_relation.return_value = []
    mock.id_info.id_column_name = "id"

    with pytest.raises(FakeAbort) as e:
        check_for_id(
            table_name=mock.table_name, id_info=mock.id_info, db_client=mock.db_client
        )

    mock.db_client._select_from_single_relation.assert_called_once_with(
        relation_name=mock.table_name,
        where_mappings=mock.id_info.where_mappings,
        columns=[mock.id_info.id_column_name],
    )
    mock_flask_response_manager.abort.assert_called_once_with(
        code=HTTPStatus.NOT_FOUND,
        message=f"Entry for {mock.id_info.where_mappings} not found.",
    )
