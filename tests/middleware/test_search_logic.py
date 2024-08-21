from http import HTTPStatus
from unittest.mock import MagicMock

from middleware.search_logic import search_wrapper
from tests.helper_scripts.DynamicMagicMock import DynamicMagicMock


class SearchWrapperMocks(DynamicMagicMock):
    make_response: MagicMock
    dictify_namedtuple: MagicMock

def test_search_wrapper(monkeypatch):
    mock = SearchWrapperMocks(
        patch_root="middleware.search_logic",
    )
    mock.db_client.search_with_location_and_record_type.return_value = mock.search_results

    mock.dictify_namedtuple.return_value = [MagicMock()]

    search_wrapper(mock.db_client, mock.dto)
    mock.db_client.search_with_location_and_record_type.assert_called_with(
        state=mock.dto.state, record_categories=mock.dto.record_categories, county=mock.dto.county, locality=mock.dto.locality
    )
    mock.dictify_namedtuple.assert_called_with(mock.search_results)
    mock.make_response.assert_called_with(
        {"count": 1, "data": mock.dictify_namedtuple.return_value}, HTTPStatus.OK)

