from http import HTTPStatus
from unittest.mock import MagicMock

from middleware.primary_resource_logic.search_logic import search_wrapper, format_search_results
from tests.helper_scripts.DynamicMagicMock import DynamicMagicMock


class SearchWrapperMocks(DynamicMagicMock):
    make_response: MagicMock
    format_search_results: MagicMock


def test_search_wrapper(monkeypatch):
    mock = SearchWrapperMocks(
        patch_root="middleware.primary_resource_logic.search_logic",
    )
    mock.db_client.search_with_location_and_record_type.return_value = (
        mock.search_results
    )

    search_wrapper(mock.db_client, mock.dto)
    mock.db_client.search_with_location_and_record_type.assert_called_with(
        state=mock.dto.state,
        record_categories=mock.dto.record_categories,
        county=mock.dto.county,
        locality=mock.dto.locality,
    )
    mock.format_search_results.assert_called_with(mock.search_results)
    mock.make_response.assert_called_with(
        mock.format_search_results.return_value, HTTPStatus.OK
    )


def test_format_search_results():
    search_results = [
        {
            "name": "test federal",
            "jurisdiction_type": "federal",
        },
        {
            "name": "test state",
            "jurisdiction_type": "state",
        },
        {
            "name": "test county",
            "jurisdiction_type": "county",
        },
        {
            "name": "test locality",
            "jurisdiction_type": "locality",
        },
        {
            "name": "another test locality",
            "jurisdiction_type": "locality",
        },
    ]

    expected_formatted_search_results = {
        "count": 5,
        "data": {
            "federal": {
                "count": 1,
                "results": [
                    {
                        "name": "test federal",
                        "jurisdiction_type": "federal",
                    }
                ],
            },
            "state": {
                "count": 1,
                "results": [
                    {
                        "name": "test state",
                        "jurisdiction_type": "state",
                    }
                ],
            },
            "county": {
                "count": 1,
                "results": [
                    {
                        "name": "test county",
                        "jurisdiction_type": "county",
                    }
                ],
            },
            "locality": {
                "count": 2,
                "results": [
                    {
                        "name": "test locality",
                        "jurisdiction_type": "locality",
                    },
                    {
                        "name": "another test locality",
                        "jurisdiction_type": "locality",
                    },
                ],
            },
        },
    }

    assert format_search_results(search_results) == expected_formatted_search_results
