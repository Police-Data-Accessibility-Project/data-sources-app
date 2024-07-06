from http import HTTPStatus
from unittest.mock import MagicMock

import pytest

from database_client.database_client import DatabaseClient
from middleware.typeahead_suggestion_logic import (
    get_typeahead_dict_results,
    get_typeahead_suggestions_wrapper,
)


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


def test_get_typeahead_suggestions_wrapper(monkeypatch):
    mock_db_client = MagicMock()
    mock_query = MagicMock()
    mock_suggestions = MagicMock()
    mock_db_client.get_typeahead_suggestions.return_value = mock_suggestions
    mock_dict_results = MagicMock()
    mock_get_typeahead_dict_results = MagicMock(return_value=mock_dict_results)
    monkeypatch.setattr(
        "middleware.typeahead_suggestion_logic.get_typeahead_dict_results",
        mock_get_typeahead_dict_results,
    )
    mock_make_response = MagicMock()
    monkeypatch.setattr(
        "middleware.typeahead_suggestion_logic.make_response", mock_make_response
    )

    get_typeahead_suggestions_wrapper(mock_db_client, mock_query)
    mock_db_client.get_typeahead_suggestions.assert_called_with(mock_query)
    mock_get_typeahead_dict_results.assert_called_with(mock_suggestions)
    mock_make_response.assert_called_with(mock_dict_results, HTTPStatus.OK)
