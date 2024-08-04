"""Integration tests for /agencies endpoint"""

from http import HTTPStatus
import psycopg2
from tests.fixtures import dev_db_connection, client_with_db
from tests.helper_scripts.helper_functions import (
    create_test_user_api,
    create_api_key,
    check_response_status,
    create_test_user_setup,
)


def test_agencies_get(
    client_with_db, dev_db_connection: psycopg2.extensions.connection
):
    """
    Test that GET call to /agencies endpoint properly retrieves a nonzero amount of data
    """

    tus = create_test_user_setup(client_with_db)
    response = client_with_db.get(
        "/api/agencies/2",
        headers=tus.authorization_header,
    )
    check_response_status(response, HTTPStatus.OK.value)
    data = response.json["data"]
    assert len(data) > 0
    assert isinstance(data[0], dict)
    assert data[0]["airtable_uid"] is not None
