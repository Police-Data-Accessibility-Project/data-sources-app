from http import HTTPStatus
from unittest.mock import MagicMock, patch, call

from middleware.homepage_search_cache import (
    get_agencies_without_homepage_urls,
    update_search_cache,
)

PATCH_ROOT = "middleware.homepage_search_cache"


@patch(f"{PATCH_ROOT}.format_list_response")
@patch(f"{PATCH_ROOT}.make_response")
def test_get_agencies_without_homepage_urls(
    mock_make_response: MagicMock, mock_format_list_response: MagicMock
):
    mock_db_client = MagicMock()

    get_agencies_without_homepage_urls(mock_db_client)

    mock_db_client.get_agencies_without_homepage_urls.assert_called_once()
    mock_format_list_response.assert_called_once_with(
        mock_db_client.get_agencies_without_homepage_urls.return_value
    )
    mock_make_response.assert_called_once_with(
        mock_format_list_response.return_value, 200
    )


@patch(f"{PATCH_ROOT}.message_response")
def test_update_search_cache(mock_message_response: MagicMock):
    mock = MagicMock()
    mock.dto.search_results = ["test_result_1", "test_result_2"]

    update_search_cache(db_client=mock.db_client, dto=mock.dto)

    assert mock.db_client.create_search_cache_entry.call_count == 2
    mock.db_client.create_search_cache_entry.assert_has_calls(
        calls=[
            call(
                column_value_mappings={
                    "agency_airtable_uid": mock.dto.agency_airtable_uid,
                    "search_result": "test_result_1",
                }
            ),
            call(
                column_value_mappings={
                    "agency_airtable_uid": mock.dto.agency_airtable_uid,
                    "search_result": "test_result_2",
                }
            ),
        ]
    )

    mock_message_response.assert_called_once_with("Search Cache Updated", HTTPStatus.OK)
