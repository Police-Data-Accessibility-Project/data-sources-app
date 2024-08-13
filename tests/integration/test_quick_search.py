"""Integration tests for /quick-search/<search>/<location>" endpoint"""

from urllib.parse import quote
from http import HTTPStatus

from tests.fixtures import flask_client_with_db, connection_with_test_data, dev_db_connection
from tests.helper_scripts.helper_functions import (
    create_test_user_api,
    create_api_key,
    check_response_status,
    create_test_user_setup,
    get_most_recent_quick_search_query_log,
)


def test_quick_search_get(flask_client_with_db, connection_with_test_data):
    """
    Test that GET call to /quick-search/<search_term>/<location> endpoint successfully retrieves a single entry with the correct agency name and airtable UID
    """

    tus = create_test_user_setup(flask_client_with_db)

    cursor = connection_with_test_data.cursor()
    cursor.execute("SELECT NOW()")
    result = cursor.fetchone()
    test_datetime = result[0]

    search_term = "Source 1"
    location = "City A"

    # URL encode the search term and location
    encoded_search_term = quote(search_term)
    encoded_location = quote(location)

    response = flask_client_with_db.get(
        f"/api/quick-search/{encoded_search_term}/{encoded_location}",
        headers=tus.api_authorization_header,
    )
    check_response_status(response, HTTPStatus.OK.value)
    data = response.json.get("data")
    assert len(data) == 1, "Quick Search endpoint response should return only one entry"
    entry = data[0]
    assert entry["agency_name"] == "Agency A"
    assert entry["airtable_uid"] == "SOURCE_UID_1"

    # Test that query inserted into log
    result = get_most_recent_quick_search_query_log(cursor, "Source 1", "City A")
    assert result.result_count == 1
    assert len(result.results) == 1
    assert result.results[0] == "SOURCE_UID_1"
    assert result.updated_at >= test_datetime

