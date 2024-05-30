import psycopg2
import pytest
from tests.fixtures import connection_with_test_data, dev_db_connection, client_with_db
from tests.helper_functions import create_test_user_api, create_api_key


def test_search_tokens_get(
    client_with_db, connection_with_test_data: psycopg2.extensions.connection
):
    user_info = create_test_user_api(client_with_db)
    api_key = create_api_key(client_with_db, user_info)
    response = client_with_db.get(
        "/search-tokens",
        headers={"Authorization": f"Bearer {api_key}"},
        query_string={
            "endpoint": "quick-search",
            "arg1": "Source 1",
            "arg2": "City A"
        }
    )
    assert response.status_code == 200
    data = response.json.get("data")
    assert data["count"] == 1, "Quick Search endpoint response should return only one entry"
    entry = data["data"][0]
    assert entry["agency_name"] == "Agency A"
    assert entry["airtable_uid"] == "SOURCE_UID_1"

