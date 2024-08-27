"""Integration tests for /agencies endpoint"""

from http import HTTPStatus
import psycopg

from database_client.database_client import DatabaseClient
from middleware.enums import PermissionsEnum
from tests.fixtures import dev_db_connection, flask_client_with_db, dev_db_client
from tests.helper_scripts.helper_functions import (
    check_response_status,
    create_test_user_setup_db_client,
    run_and_validate_request,
)


def test_agencies_get(flask_client_with_db, dev_db_client: DatabaseClient):
    """
    Test that GET call to /agencies endpoint properly retrieves a nonzero amount of data
    """
    tus = create_test_user_setup_db_client(dev_db_client)

    response_json = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint="/api/agencies/page/2",
        headers=tus.api_authorization_header,
    )

    data = response_json["data"]
    assert len(data) > 0
    assert isinstance(data[0], dict)
    assert data[0]["airtable_uid"] is not None
