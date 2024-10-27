from http import HTTPStatus
from unittest.mock import MagicMock

from middleware.primary_resource_logic.search_logic import (
    search_wrapper,
    format_search_results,
)
from tests.helper_scripts.DynamicMagicMock import DynamicMagicMock


class SearchWrapperMocks(DynamicMagicMock):
    make_response: MagicMock
    format_search_results: MagicMock

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
