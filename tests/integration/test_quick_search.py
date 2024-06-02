"""Integration tests for /quick-search/<search>/<location>" endpoint"""

from urllib.parse import quote

from tests.fixtures import dev_db_connection, client_with_db, connection_with_test_data
from tests.helper_functions import (
    create_test_user_api,
    create_api_key,
    check_response_status,
)


def test_quick_search_get(client_with_db, connection_with_test_data):
    """
    Test that GET call to /quick-search/<search_term>/<location> endpoint successfully retrieves a single entry with the correct agency name and airtable UID
    """

    user_info = create_test_user_api(client_with_db)
    api_key = create_api_key(client_with_db, user_info)

    search_term = "Source 1"
    location = "City A"

    # URL encode the search term and location
    encoded_search_term = quote(search_term)
    encoded_location = quote(location)

    response = client_with_db.get(
        f"/quick-search/{encoded_search_term}/{encoded_location}",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    check_response_status(response, 200)
    data = response.json.get("data")
    assert (
        data["count"] == 1
    ), "Quick Search endpoint response should return only one entry"
    entry = data["data"][0]
    assert entry["agency_name"] == "Agency A"
    assert entry["airtable_uid"] == "SOURCE_UID_1"
