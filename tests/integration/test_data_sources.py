"""Integration tests for /data-sources endpoint"""

from http import HTTPStatus
import uuid

import psycopg2

from database_client.database_client import DatabaseClient
from middleware.enums import PermissionsEnum
from tests.fixtures import (
    connection_with_test_data,
    dev_db_connection,
    flask_client_with_db,
    db_client_with_test_data,
)
from tests.helper_scripts.helper_functions import (
    get_boolean_dictionary,
    create_test_user_api,
    create_api_key,
    give_user_admin_role,
    check_response_status,
    create_test_user_setup,
    create_test_user_setup_db_client,
)


def test_data_sources_get(
        flask_client_with_db, connection_with_test_data: psycopg2.extensions.connection
):
    """
    Test that GET call to /data-sources endpoint retrieves data sources and correctly identifies specific sources by name
    """
    inserted_data_sources_found = get_boolean_dictionary(
        ("Source 1", "Source 2", "Source 3")
    )
    tus = create_test_user_setup(flask_client_with_db)
    response = flask_client_with_db.get(
        "/api/data-sources",
        headers=tus.authorization_header,
    )
    check_response_status(response, HTTPStatus.OK.value)
    data = response.get_json()["data"]
    for result in data:
        name = result["name"]
        if name in inserted_data_sources_found:
            inserted_data_sources_found[name] = True
    assert inserted_data_sources_found["Source 1"]
    assert not inserted_data_sources_found["Source 2"]
    assert not inserted_data_sources_found["Source 3"]


def test_data_sources_post(flask_client_with_db, db_client_with_test_data: DatabaseClient):
    """
    Test that POST call to /data-sources endpoint successfully creates a new data source with a unique name and verifies its existence in the database
    """

    tus = create_test_user_setup_db_client(
        db_client_with_test_data,
        permission=PermissionsEnum.DB_WRITE,
    )

    name = str(uuid.uuid4())
    response = flask_client_with_db.post(
        "/data-sources",
        json={"name": name},
        headers=tus.authorization_header,
    )
    check_response_status(response, HTTPStatus.OK.value)
    cursor = db_client_with_test_data.cursor
    cursor.execute(
        """
    SELECT * from data_sources WHERE name=%s
    """,
        (name,),
    )
    rows = cursor.fetchall()
    assert (len(rows)) == 1
