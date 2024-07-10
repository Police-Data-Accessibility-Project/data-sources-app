from http import HTTPStatus
from unittest.mock import MagicMock

from middleware.agencies import (
    get_agencies_matches,
    get_agencies,
)
from tests.helper_functions import DynamicMagicMock

class AgenciesMocks(DynamicMagicMock):
    db_client: MagicMock
    page: MagicMock
    results: MagicMock

def test_get_agencies_matches(monkeypatch):
    mock = AgenciesMocks()
    mock.db_client.get_agencies_from_page = MagicMock(return_value=mock.results)
    mock_process_results = MagicMock(return_value=mock.results)

    # Use monkeypatch to set mock values
    monkeypatch.setattr("middleware.agencies.process_results", mock_process_results)

    # Call function
    results = get_agencies_matches(mock.db_client, mock.page)

    # Check results
    assert results == mock.results
    mock.db_client.get_agencies_from_page.assert_called_once_with(mock.page)
    mock_process_results.assert_called_once_with(mock.results)


def test_get_agencies(monkeypatch):
    mock = AgenciesMocks()

    # Create Mock values
    mock_agencies_matches = [MagicMock() for _ in range(3)]
    mock_get_agencies_matches = MagicMock(return_value=mock_agencies_matches)
    mock_make_response = MagicMock(return_value=mock.response)

    monkeypatch.setattr("middleware.agencies.get_agencies_matches", mock_get_agencies_matches)
    monkeypatch.setattr("middleware.agencies.make_response", mock_make_response)

    # Call function
    response = get_agencies(mock.db_client, mock.page)

    # Check results
    assert response == mock.response
    mock_get_agencies_matches.assert_called_once_with(mock.db_client, mock.page)
    mock_make_response.assert_called_once_with(
        {"count": len(mock_agencies_matches), "data": mock_agencies_matches},
        HTTPStatus.OK,
    )
