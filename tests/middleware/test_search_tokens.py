from unittest.mock import MagicMock

import pytest

from middleware.search_tokens_logic import perform_endpoint_logic, UnknownEndpointError
from tests.helper_functions import DynamicMagicMock


class SearchTokensLogicMocks(DynamicMagicMock):
    arg1: MagicMock
    arg2: MagicMock
    endpoint_str: MagicMock
    conn: MagicMock
    quick_search_query_wrapper: MagicMock
    get_approved_data_sources_wrapper: MagicMock
    data_source_by_id_wrapper: MagicMock
    get_data_sources_for_map_wrapper: MagicMock


@pytest.fixture
def mocks(monkeypatch):
    mocks = SearchTokensLogicMocks()
    monkeypatch.setattr(
        "middleware.search_tokens_logic.quick_search_query_wrapper",
        mocks.quick_search_query_wrapper,
    )
    monkeypatch.setattr(
        "middleware.search_tokens_logic.get_approved_data_sources_wrapper",
        mocks.get_approved_data_sources_wrapper,
    )
    monkeypatch.setattr(
        "middleware.search_tokens_logic.data_source_by_id_wrapper",
        mocks.data_source_by_id_wrapper,
    )
    monkeypatch.setattr(
        "middleware.search_tokens_logic.get_data_sources_for_map_wrapper",
        mocks.get_data_sources_for_map_wrapper,
    )
    return mocks


def test_perform_endpoint_logic_quick_search(mocks):
    perform_endpoint_logic(mocks.arg1, mocks.arg2, "quick-search", mocks.conn)

    mocks.quick_search_query_wrapper.assert_called_once_with(
        mocks.arg1, mocks.arg2, mocks.conn
    )
    mocks.get_approved_data_sources_wrapper.assert_not_called()
    mocks.data_source_by_id_wrapper.assert_not_called()
    mocks.get_data_sources_for_map_wrapper.assert_not_called()


def test_perform_endpoint_logic_data_sources(mocks):
    perform_endpoint_logic(mocks.arg1, mocks.arg2, "data-sources", mocks.conn)

    mocks.quick_search_query_wrapper.assert_not_called()
    mocks.get_approved_data_sources_wrapper.assert_called_once_with(mocks.conn)
    mocks.data_source_by_id_wrapper.assert_not_called()
    mocks.get_data_sources_for_map_wrapper.assert_not_called()


def test_perform_endpoint_logic_data_sources_by_id(mocks):
    perform_endpoint_logic(mocks.arg1, mocks.arg2, "data-sources-by-id", mocks.conn)

    mocks.quick_search_query_wrapper.assert_not_called()
    mocks.get_approved_data_sources_wrapper.assert_not_called()
    mocks.data_source_by_id_wrapper.assert_called_once_with(mocks.arg1, mocks.conn)
    mocks.get_data_sources_for_map_wrapper.assert_not_called()


def test_perform_endpoint_logic_data_sources_map(mocks):
    perform_endpoint_logic(mocks.arg1, mocks.arg2, "data-sources-map", mocks.conn)

    mocks.quick_search_query_wrapper.assert_not_called()
    mocks.get_approved_data_sources_wrapper.assert_not_called()
    mocks.data_source_by_id_wrapper.assert_not_called()
    mocks.get_data_sources_for_map_wrapper.assert_called_once_with(mocks.conn)


def test_perform_endpoint_logic_unknown_endpoint(mocks):
    with pytest.raises(UnknownEndpointError):
        perform_endpoint_logic(mocks.arg1, mocks.arg2, "unknown-endpoint", mocks.conn)

    mocks.quick_search_query_wrapper.assert_not_called()
    mocks.get_approved_data_sources_wrapper.assert_not_called()
    mocks.data_source_by_id_wrapper.assert_not_called()
    mocks.get_data_sources_for_map_wrapper.assert_not_called()
