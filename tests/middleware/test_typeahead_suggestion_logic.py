from http import HTTPStatus
from unittest.mock import MagicMock

from database_client.database_client import DatabaseClient
from middleware.primary_resource_logic.typeahead_suggestion_logic import (
    get_typeahead_dict_results,
    get_typeahead_suggestions_wrapper,
)
from tests.helper_scripts.DynamicMagicMock import DynamicMagicMock


def test_get_typeahead_dict_results():
    mock_suggestions = [
        DatabaseClient.TypeaheadSuggestions(
            display_name="display_name_1",
            type="type_1",
            state="state_1",
            county="county_1",
            locality="locality_1",
        ),
        DatabaseClient.TypeaheadSuggestions(
            display_name="display_name_2",
            type="type_2",
            state="state_2",
            county="county_2",
            locality="locality_2",
        ),
        DatabaseClient.TypeaheadSuggestions(
            display_name="display_name_3",
            type="type_3",
            state="state_3",
            county="county_3",
            locality="locality_3",
        ),
    ]

    expected_results = [
        {
            "display_name": "display_name_1",
            "type": "type_1",
            "state": "state_1",
            "county": "county_1",
            "locality": "locality_1",
        },
        {
            "display_name": "display_name_2",
            "type": "type_2",
            "state": "state_2",
            "county": "county_2",
            "locality": "locality_2",
        },
        {
            "display_name": "display_name_3",
            "type": "type_3",
            "state": "state_3",
            "county": "county_3",
            "locality": "locality_3",
        },
    ]

    assert get_typeahead_dict_results(mock_suggestions) == expected_results


class GetTypeaheadSuggestionsMocks(DynamicMagicMock):
    get_typeahead_dict_results: MagicMock
    make_response: MagicMock


def test_get_typeahead_suggestions_wrapper(monkeypatch):
    mock = GetTypeaheadSuggestionsMocks(
        patch_root="middleware.primary_resource_logic.typeahead_suggestion_logic",
    )

    get_typeahead_suggestions_wrapper(mock.db_client, mock.query)

    mock.db_client.get_typeahead_suggestions.assert_called_with(mock.query)
    mock.get_typeahead_dict_results.assert_called_with(
        mock.db_client.get_typeahead_suggestions.return_value
    )
    mock.make_response.assert_called_with(
        {"suggestions": mock.get_typeahead_dict_results.return_value}, HTTPStatus.OK
    )
