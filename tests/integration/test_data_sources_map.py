"""Integration tests for /data-sources-map endpoint"""

from http import HTTPStatus
import psycopg2
from tests.fixtures import connection_with_test_data, dev_db_connection, client_with_db
from tests.helper_functions import (
    create_test_user_api,
    create_api_key,
    check_response_status,
)


def test_data_sources_map_get(
    client_with_db, connection_with_test_data: psycopg2.extensions.connection
):
    """
    Test that GET call to /data-sources-map endpoint retrieves data sources and verifies the location (latitude and longitude) of a specific source by name
    """
    user_info = create_test_user_api(client_with_db)
    api_key = create_api_key(client_with_db, user_info)
    response = client_with_db.get(
        "/data-sources-map",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    check_response_status(response, HTTPStatus.OK.value)
    data = response.json["data"]
    found_source = False
    for result in data:
        name = result["name"]
        if name != "Source 1":
            continue
        found_source = True
        assert result["lat"] == 30
        assert result["lng"] == 20
    assert found_source
