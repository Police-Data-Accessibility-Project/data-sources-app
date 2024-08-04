"""Integration tests for /search-tokens endpoint."""

import psycopg2
from http import HTTPStatus
from tests.fixtures import connection_with_test_data, client_with_db, dev_db_connection
from tests.helper_scripts.helper_functions import (
    create_test_user_api,
    create_api_key,
    check_response_status,
    create_test_user_setup,
)


def test_search_tokens_get(
    client_with_db, connection_with_test_data: psycopg2.extensions.connection
):
    """
    Test that GET call to /search-tokens endpoint with specified query parameters successfully retrieves search tokens and verifies the correct entry with agency name and airtable UID
    """
    tus = create_test_user_setup(client_with_db)
    response = client_with_db.get(
        "/api/search-tokens",
        headers=tus.authorization_header,
        query_string={"endpoint": "quick-search", "arg1": "Source 1", "arg2": "City A"},
    )
    check_response_status(response, HTTPStatus.OK.value)
    data = response.json.get("data")
    assert len(data) == 1, "Quick Search endpoint response should return only one entry"
    entry = data[0]
    assert entry["agency_name"] == "Agency A"
    assert entry["airtable_uid"] == "SOURCE_UID_1"
