"""Integration tests for /agencies endpoint"""

from http import HTTPStatus
import psycopg2
from tests.fixtures import dev_db_connection, client_with_db
from tests.helper_functions import (
    create_test_user_api,
    create_api_key,
    check_response_status,
)


def test_agencies_get(
    client_with_db, dev_db_connection: psycopg2.extensions.connection
):
    """
    Test that GET call to /agencies endpoint properly retrieves a nonzero amount of data
    """

    user_info = create_test_user_api(client_with_db)
    api_key = create_api_key(client_with_db, user_info)
    response = client_with_db.get(
        "/api/agencies/2",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    check_response_status(response, HTTPStatus.OK.value)
    data = response.json["data"]
    assert len(data) > 0
    assert isinstance(data[0], dict)
