from http import HTTPStatus
from unittest.mock import MagicMock

from middleware.search_logic import search_wrapper


def test_search_wrapper(monkeypatch):
    mock_search_results = MagicMock()
    mock_db_client = MagicMock()
    mock_db_client.search_with_location_and_record_type.return_value = mock_search_results
    mock_state = MagicMock()
    mock_record_type = MagicMock()
    mock_county = MagicMock()
    mock_locality = MagicMock()

    mock_dict_results = MagicMock()
    mock_dictify_namedtuple = MagicMock()
    mock_dictify_namedtuple.return_value = [mock_dict_results]
    monkeypatch.setattr("middleware.search_logic.dictify_namedtuple", mock_dictify_namedtuple)
    mock_make_response = MagicMock()

    monkeypatch.setattr("middleware.search_logic.make_response", mock_make_response)
    search_wrapper(mock_db_client, mock_state, mock_record_type, mock_county, mock_locality)
    mock_db_client.search_with_location_and_record_type.assert_called_with(
        state=mock_state, record_type=mock_record_type, county=mock_county, locality=mock_locality
    )
    mock_dictify_namedtuple.assert_called_with(mock_search_results)
    mock_make_response.assert_called_with(
        {"count": 1, "data": [mock_dict_results]}, HTTPStatus.OK)

