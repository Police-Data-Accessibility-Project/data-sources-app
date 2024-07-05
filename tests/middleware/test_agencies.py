from http import HTTPStatus
from unittest.mock import MagicMock

from middleware.agencies import (
    get_agencies_matches,
    get_agencies,
)



def test_get_agencies_matches(monkeypatch):
    mock_db_client = MagicMock()
    mock_page = MagicMock()
    mock_results = MagicMock()
    mock_db_client.get_agencies_from_page = MagicMock(return_value=mock_results)
    mock_process_results = MagicMock(return_value=mock_results)

    # Use monkeypatch to set mock values
    monkeypatch.setattr("middleware.agencies.process_results", mock_process_results)

    # Call function
    results = get_agencies_matches(mock_db_client, mock_page)

    # Check results
    assert results == mock_results
    mock_db_client.get_agencies_from_page.assert_called_once_with(mock_page)
    mock_process_results.assert_called_once_with(mock_results)


def test_get_agencies(monkeypatch):

    # Create Mock values
    mock_db_client = MagicMock()
    mock_page = MagicMock()
    mock_agencies_matches = [MagicMock() for _ in range(3)]
    mock_get_agencies_matches = MagicMock(return_value=mock_agencies_matches)
    mock_response = MagicMock()
    mock_make_response = MagicMock(return_value=mock_response)

    monkeypatch.setattr("middleware.agencies.get_agencies_matches", mock_get_agencies_matches)
    monkeypatch.setattr("middleware.agencies.make_response", mock_make_response)

    # Call function
    response = get_agencies(mock_db_client, mock_page)

    # Check results
    assert response == mock_response
    mock_get_agencies_matches.assert_called_once_with(mock_db_client, mock_page)
    mock_make_response.assert_called_once_with(
        {"count": len(mock_agencies_matches), "data": mock_agencies_matches},
        HTTPStatus.OK,
    )
