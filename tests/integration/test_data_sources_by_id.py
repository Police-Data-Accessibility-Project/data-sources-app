"""Integration tests for /data-sources-by-id endpoint"""

from http import HTTPStatus
import uuid
import psycopg2
from psycopg2.extras import DictCursor

from database_client.database_client import DatabaseClient
from tests.fixtures import (
    connection_with_test_data,
    flask_client_with_db,
    dev_db_connection,
    db_client_with_test_data,
    test_user_admin
)
from tests.helper_scripts.helper_functions import (
    create_test_user_api,
    create_api_key,
    give_user_admin_role,
    check_response_status,
    create_test_user_setup,
    create_test_user_setup_db_client,
)


def test_data_sources_by_id_get(
        flask_client_with_db, connection_with_test_data: psycopg2.extensions.connection
):
    """
    Test that GET call to /data-sources-by-id/<data_source_id> endpoint retrieves the data source with the correct homepage URL
    """

    tus = create_test_user_setup(flask_client_with_db)
    response = flask_client_with_db.get(
        "/api/data-sources-by-id/SOURCE_UID_1",
        headers=tus.api_authorization_header,
    )
    check_response_status(response, HTTPStatus.OK.value)
    assert response.json["source_url"] == "http://src1.com"


def test_data_sources_by_id_put(
        flask_client_with_db, db_client_with_test_data: DatabaseClient, test_user_admin
):
    """
    Test that PUT call to /data-sources-by-id/<data_source_id> endpoint successfully updates the description of the data source and verifies the change in the database
    """

    desc = str(uuid.uuid4())
    response = flask_client_with_db.put(
        f"/api/data-sources-by-id/SOURCE_UID_1",
        headers=test_user_admin.jwt_authorization_header,
        json={"description": desc},
    )
    assert response.status_code == HTTPStatus.OK.value
    cursor = db_client_with_test_data.cursor
    db_client = DatabaseClient(cursor)
    result = db_client.get_data_source_by_id("SOURCE_UID_1")
    assert result["description"] == desc
