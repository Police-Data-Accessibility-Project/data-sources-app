"""Integration tests for /api_key endpoint"""

from http import HTTPStatus
import uuid

import psycopg2.extensions

from tests.fixtures import dev_db_connection, client_with_db
from tests.helper_functions import create_test_user_api


def test_api_key_get(client_with_db, dev_db_connection: psycopg2.extensions.connection):
    """
    Test that GET call to /api_key endpoint successfully creates an API key and aligns it with the user's API key in the database
    """

    user_info = create_test_user_api(client_with_db)

    response = client_with_db.get(
        "/api_key",
        json={"email": user_info.email, "password": user_info.password},
    )
    assert (
        response.status_code == HTTPStatus.OK.value
    ), "API key creation not successful"

    # Check that API key aligned with user
    cursor = dev_db_connection.cursor()
    cursor.execute(
        """
        SELECT api_key from users where email = %s
        """,
        (user_info.email,),
    )
    db_api_key = cursor.fetchone()[0]
    assert db_api_key == response.json.get(
        "api_key"
    ), "API key returned not aligned with user API key in database"
