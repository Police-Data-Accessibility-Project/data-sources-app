"""Integration tests for /data-sources-needs-identification endpoint"""

from http import HTTPStatus
import psycopg
from tests.fixtures import (
    connection_with_test_data,
    flask_client_with_db,
    dev_db_connection,
)
from tests.helper_scripts.helper_functions import (
    get_boolean_dictionary,
    create_test_user_api,
    create_api_key,
    check_response_status,
    create_test_user_setup,
    run_and_validate_request,
    search_with_boolean_dictionary,
)


def test_data_sources_needs_identification(
    flask_client_with_db, connection_with_test_data: psycopg.connection
):
    """
    Test that GET call to /data-sources-needs-identification endpoint retrieves data sources that need identification and correctly identifies specific sources by name
    """
    inserted_data_sources_found = get_boolean_dictionary(
        ("Source 1", "Source 2", "Source 3")
    )
    tus = create_test_user_setup(flask_client_with_db)
    response_json = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint="/api/data-sources-needs-identification",
        headers=tus.api_authorization_header,
    )

    data = response_json["data"]
    search_with_boolean_dictionary(
        data=data,
        boolean_dictionary=inserted_data_sources_found,
        key_to_search_on="name",
    )

    assert not inserted_data_sources_found["Source 1"]
    assert inserted_data_sources_found["Source 2"]
    assert not inserted_data_sources_found["Source 3"]
