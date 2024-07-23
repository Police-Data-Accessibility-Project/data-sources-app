from http import HTTPStatus

import psycopg2

from tests.fixtures import dev_db_connection, client_with_db
from tests.helper_functions import check_response_status


def test_auth_get(
    client_with_db, dev_db_connection: psycopg2.extensions.connection
):
    """
    Test that GET call to /auth endpoint successfully retrieves a non-zero amount of data
    """
    response = client_with_db.get("/api/auth/authorize")
    check_response_status(response, HTTPStatus.OK.value)
    assert len(response.json) > 0