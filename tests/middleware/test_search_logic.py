from http import HTTPStatus
from unittest.mock import MagicMock

from middleware.search_logic import search_wrapper
from tests.helper_scripts.DymamicMagicMock import DynamicMagicMock


class SearchWrapperMocks(DynamicMagicMock):
    db_client: MagicMock
    state: MagicMock
    record_type: MagicMock
    county: MagicMock
    locality: MagicMock
    make_response: MagicMock
    search_results: MagicMock
    dictify_namedtuple: MagicMock

def test_search_wrapper(monkeypatch):
    mock = SearchWrapperMocks(
        patch_root="middleware.search_logic",
        mocks_to_patch=["make_response", "dictify_namedtuple"],
    )
    mock.db_client.search_with_location_and_record_type.return_value = mock.search_results

    mock.dictify_namedtuple.return_value = [MagicMock()]

    search_wrapper(mock.db_client, mock.state, mock.record_type, mock.county, mock.locality)
    mock.db_client.search_with_location_and_record_type.assert_called_with(
        state=mock.state, record_type=mock.record_type, county=mock.county, locality=mock.locality
    )
    mock.dictify_namedtuple.assert_called_with(mock.search_results)
    mock.make_response.assert_called_with(
        {"count": 1, "data": mock.dictify_namedtuple.return_value}, HTTPStatus.OK)

