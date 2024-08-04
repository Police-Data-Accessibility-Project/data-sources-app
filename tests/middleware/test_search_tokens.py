from unittest.mock import MagicMock

import pytest

from middleware.search_tokens_logic import perform_endpoint_logic, UnknownEndpointError
from tests.helper_scripts.DymamicMagicMock import DynamicMagicMock


class SearchTokensLogicMocks(DynamicMagicMock):
    arg1: MagicMock
    arg2: MagicMock
    endpoint_str: MagicMock
    conn: MagicMock
    quick_search_query_wrapper: MagicMock
    get_approved_data_sources_wrapper: MagicMock
    data_source_by_id_wrapper: MagicMock
    get_data_sources_for_map_wrapper: MagicMock

SEARCH_TOKENS_LOGIC_MOCKS_PATCH_ROOT = "middleware.search_tokens_logic"

@pytest.fixture
def mocks(monkeypatch):
    mocks = SearchTokensLogicMocks(
        patch_root=SEARCH_TOKENS_LOGIC_MOCKS_PATCH_ROOT,
        mocks_to_patch=["quick_search_query_wrapper", "get_approved_data_sources_wrapper", "data_source_by_id_wrapper", "get_data_sources_for_map_wrapper"],
    )
    return mocks

def _perform_logic_and_verify(
        mocks,
        endpoint,
        raises_exception=False,
        called_mock=None,
        *called_with):

    if raises_exception:
        with pytest.raises(UnknownEndpointError):
            perform_endpoint_logic(mocks.arg1, mocks.arg2, endpoint, mocks.conn)
    else:
        perform_endpoint_logic(mocks.arg1, mocks.arg2, endpoint, mocks.conn)

    # Create a dictionary of all mocks and whether they should have been called
    expected_calls = {
        "quick_search_query_wrapper": mocks.quick_search_query_wrapper,
        "get_approved_data_sources_wrapper": mocks.get_approved_data_sources_wrapper,
        "data_source_by_id_wrapper": mocks.data_source_by_id_wrapper,
        "get_data_sources_for_map_wrapper": mocks.get_data_sources_for_map_wrapper,
    }

    for name, mock in expected_calls.items():
        if name == called_mock:
            mock.assert_called_once_with(*called_with)
        else:
            mock.assert_not_called()

def test_perform_endpoint_logic_quick_search(mocks):
    _perform_logic_and_verify(
        mocks, "quick-search", False, "quick_search_query_wrapper", mocks.arg1, mocks.arg2, mocks.conn
    )

def test_perform_endpoint_logic_data_sources(mocks):
    _perform_logic_and_verify(
        mocks, "data-sources", False, "get_approved_data_sources_wrapper", mocks.conn
    )

def test_perform_endpoint_logic_data_sources_by_id(mocks):
    _perform_logic_and_verify(
        mocks, "data-sources-by-id", False, "data_source_by_id_wrapper", mocks.arg1, mocks.conn
    )

def test_perform_endpoint_logic_data_sources_map(mocks):
    _perform_logic_and_verify(
        mocks, "data-sources-map", False, "get_data_sources_for_map_wrapper", mocks.conn
    )

def test_perform_endpoint_logic_unknown_endpoint(mocks):
    # Since it's an unknown endpoint, none of the mocks should be called
    _perform_logic_and_verify(mocks, "unknown-endpoint", True)
