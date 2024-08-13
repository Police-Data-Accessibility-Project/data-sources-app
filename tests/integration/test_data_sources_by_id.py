"""Integration tests for /data-sources-by-id endpoint"""

from http import HTTPStatus
import uuid
import psycopg2
from psycopg2.extras import DictCursor

from conftest import test_client, session
from database_client.database_client import DatabaseClient
from tests.fixtures import connection_with_test_data, client_with_db, dev_db_connection
from tests.helper_scripts.helper_functions import (
    create_test_user_api,
    create_api_key,
    give_user_admin_role,
    check_response_status,
    create_test_user_setup,
)


def test_data_sources_by_id_get(
    client_with_db, connection_with_test_data: psycopg2.extensions.connection
):
    """
    Test that GET call to /data-sources-by-id/<data_source_id> endpoint retrieves the data source with the correct homepage URL
    """

    tus = create_test_user_setup(client_with_db)
    response = client_with_db.get(
        "/api/data-sources-by-id/SOURCE_UID_1",
        headers=tus.authorization_header,
    )
    check_response_status(response, HTTPStatus.OK.value)
    assert response.json["source_url"] == "http://src1.com"


def test_data_sources_by_id_put(
    client_with_db, connection_with_test_data: psycopg2.extensions.connection, test_client, session
):
    """
    Test that PUT call to /data-sources-by-id/<data_source_id> endpoint successfully updates the description of the data source and verifies the change in the database
    """
    tus = create_test_user_setup(client_with_db)
    give_user_admin_role(session, tus.user_info)
    desc = str(uuid.uuid4())
    response = client_with_db.put(
        f"/api/data-sources-by-id/SOURCE_UID_1",
        headers=tus.authorization_header,
        json={"description": desc},
    )
    assert response.status_code == HTTPStatus.OK.value
    cursor = connection_with_test_data.cursor(cursor_factory=DictCursor)
    db_client = DatabaseClient(cursor, session)
    result = db_client.get_data_source_by_id("SOURCE_UID_1")
    assert result["description"] == desc
