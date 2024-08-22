"""Integration tests for /data-sources-map endpoint"""

from http import HTTPStatus
import psycopg2
from tests.fixtures import (
    connection_with_test_data,
    flask_client_with_db,
    dev_db_connection,
)
from tests.helper_scripts.helper_functions import (
    create_test_user_api,
    create_api_key,
    check_response_status,
    create_test_user_setup,
    run_and_validate_request,
)


def test_data_sources_map_get(
    flask_client_with_db, connection_with_test_data: psycopg2.extensions.connection
):
    """
    Test that GET call to /data-sources-map endpoint retrieves data sources and verifies the location (latitude and longitude) of a specific source by name
    """
    tus = create_test_user_setup(flask_client_with_db)
    response_json = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint="/api/data-sources-map",
        headers=tus.api_authorization_header,
    )
    data = response_json["data"]
    found_source = False
    for result in data:
        name = result["name"]
        if name != "Source 1":
            continue
        found_source = True
        assert result["lat"] == 30
        assert result["lng"] == 20
    assert found_source
