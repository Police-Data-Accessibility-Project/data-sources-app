from http import HTTPStatus
from unittest.mock import MagicMock

import pytest

from middleware.agencies import (
    get_agencies_matches,
    get_agencies,
)
from tests.helper_scripts.DynamicMagicMock import DynamicMagicMock


class AgenciesMocks(DynamicMagicMock):
    process_results: MagicMock
    get_agencies_matches: MagicMock
    make_response: MagicMock

@pytest.fixture
def agencies_mocks():
    return AgenciesMocks(
        patch_root="middleware.agencies",
    )



def test_get_agencies_matches(monkeypatch, agencies_mocks):
    mock = agencies_mocks
    mock.db_client.get_agencies_from_page = MagicMock(return_value=mock.results)
    mock.process_results.return_value = mock.results

    # Call function
    results = get_agencies_matches(mock.db_client, mock.page)

    # Check results
    assert results == mock.results
    mock.db_client.get_agencies_from_page.assert_called_once_with(mock.page)
    mock.process_results.assert_called_once_with(mock.results)


def test_get_agencies(monkeypatch, agencies_mocks):
    mock = agencies_mocks

    # Create Mock values
    mock_agencies_matches = [MagicMock() for _ in range(3)]
    mock.get_agencies_matches.return_value = mock_agencies_matches
    mock.make_response.return_value = mock.response

    # Call function
    response = get_agencies(mock.db_client, mock.page)

    # Check results
    assert response == mock.make_response.return_value
    mock.get_agencies_matches.assert_called_once_with(mock.db_client, mock.page)
    mock.make_response.assert_called_once_with(
        {"count": len(mock_agencies_matches), "data": mock_agencies_matches},
        HTTPStatus.OK,
    )
