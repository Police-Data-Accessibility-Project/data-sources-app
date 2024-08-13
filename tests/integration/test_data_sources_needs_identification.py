"""Integration tests for /data-sources-needs-identification endpoint"""

from http import HTTPStatus
import psycopg2
from tests.fixtures import connection_with_test_data, flask_client_with_db, dev_db_connection
from tests.helper_scripts.helper_functions import (
    get_boolean_dictionary,
    create_test_user_api,
    create_api_key,
    check_response_status,
    create_test_user_setup,
)


def test_data_sources_needs_identification(
        flask_client_with_db, connection_with_test_data: psycopg2.extensions.connection
):
    """
    Test that GET call to /data-sources-needs-identification endpoint retrieves data sources that need identification and correctly identifies specific sources by name
    """
    inserted_data_sources_found = get_boolean_dictionary(
        ("Source 1", "Source 2", "Source 3")
    )
    tus = create_test_user_setup(flask_client_with_db)
    response = flask_client_with_db.get(
        "/api/data-sources-needs-identification",
        headers=tus.api_authorization_header,
    )
    check_response_status(response, HTTPStatus.OK.value)

    for result in response.json["data"]:
        name = result["name"]
        if name in inserted_data_sources_found:
            inserted_data_sources_found[name] = True

    assert not inserted_data_sources_found["Source 1"]
    assert inserted_data_sources_found["Source 2"]
    assert not inserted_data_sources_found["Source 3"]
