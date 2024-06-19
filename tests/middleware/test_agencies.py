from datetime import datetime
from http import HTTPStatus
from unittest.mock import MagicMock

import pytest

from middleware.agencies import (
    get_offset,
    execute_agency_query,
    AGENCY_SELECT_QUERY,
    process_results,
    get_agencies_matches,
    get_agencies,
)


def test_get_offset():
    assert get_offset(3) == 2000


def test_execute_agency_query(monkeypatch):

    # Create Mock values
    mock_cursor = MagicMock()
    mock_page = MagicMock()
    mock_results = MagicMock()
    mock_offset = MagicMock()
    mock_get_offset = MagicMock(return_value=mock_offset)
    mock_cursor.fetchall = MagicMock(return_value=mock_results)

    # Use monkeypatch to set mock values
    monkeypatch.setattr("middleware.agencies.get_offset", mock_get_offset)

    # Call function
    results = execute_agency_query(mock_cursor, mock_page)

    # Check results
    assert results == mock_results
    mock_cursor.fetchall.assert_called_once()
    mock_cursor.execute.assert_called_once_with(
        AGENCY_SELECT_QUERY,
        (mock_offset,),
    )


def test_process_results(monkeypatch):
    mock_results = [MagicMock() for _ in range(3)]
    mock_convert_dates_to_strings = MagicMock()

    # Monkeypatch
    monkeypatch.setattr(
        "middleware.agencies.convert_dates_to_strings", mock_convert_dates_to_strings
    )

    # Call function
    results = process_results(mock_results)

    # Check results
    assert results == mock_results
    expected_calls = [((mock_result,),) for mock_result in mock_results]
    mock_convert_dates_to_strings.assert_has_calls(expected_calls)


def test_get_agencies_matches(monkeypatch):
    mock_cursor = MagicMock()
    mock_page = MagicMock()
    mock_results = MagicMock()
    mock_execute_agency_query = MagicMock(return_value=mock_results)
    mock_process_results = MagicMock(return_value=mock_results)

    # Use monkeypatch to set mock values
    monkeypatch.setattr(
        "middleware.agencies.execute_agency_query", mock_execute_agency_query
    )
    monkeypatch.setattr("middleware.agencies.process_results", mock_process_results)

    # Call function
    results = get_agencies_matches(mock_cursor, mock_page)

    # Check results
    assert results == mock_results
    mock_execute_agency_query.assert_called_once_with(mock_cursor, mock_page)
    mock_process_results.assert_called_once_with(mock_results)


def test_get_agencies(monkeypatch):

    # Create Mock values
    mock_cursor = MagicMock()
    mock_page = MagicMock()
    mock_agencies_matches = [MagicMock() for _ in range(3)]
    mock_get_agencies_matches = MagicMock(return_value=mock_agencies_matches)
    mock_response = MagicMock()
    mock_make_response = MagicMock(return_value=mock_response)

    # Use monkeypatch to set mock values
    monkeypatch.setattr(
        "middleware.agencies.get_agencies_matches", mock_get_agencies_matches
    )
    monkeypatch.setattr("middleware.agencies.make_response", mock_make_response)

    # Call function
    response = get_agencies(mock_cursor, mock_page)

    # Check results
    assert response == mock_response
    mock_get_agencies_matches.assert_called_once_with(mock_cursor, mock_page)
    mock_make_response.assert_called_once_with(
        {"count": len(mock_agencies_matches), "data": mock_agencies_matches},
        HTTPStatus.OK,
    )
