"""Integration tests for /search-tokens endpoint."""

import psycopg2
import pytest
from tests.fixtures import connection_with_test_data, dev_db_connection, client_with_db
from tests.helper_functions import (
    create_test_user_api,
    create_api_key,
    check_response_status,
)


def test_search_tokens_get(
    client_with_db, connection_with_test_data: psycopg2.extensions.connection
):
    """
    Test that GET call to /search-tokens endpoint with specified query parameters successfully retrieves search tokens and verifies the correct entry with agency name and airtable UID
    """
    user_info = create_test_user_api(client_with_db)
    api_key = create_api_key(client_with_db, user_info)
    response = client_with_db.get(
        "/search-tokens",
        headers={"Authorization": f"Bearer {api_key}"},
        query_string={"endpoint": "quick-search", "arg1": "Source 1", "arg2": "City A"},
    )
    check_response_status(response, 200)
    data = response.json.get("data")
    assert len(data) == 1, "Quick Search endpoint response should return only one entry"
    entry = data[0]
    assert entry["agency_name"] == "Agency A"
    assert entry["airtable_uid"] == "SOURCE_UID_1"
