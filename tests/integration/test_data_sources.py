"""Integration tests for /data-sources endpoint"""

from http import HTTPStatus
import uuid

import psycopg2
from tests.fixtures import (
    connection_with_test_data,
    dev_db_connection,
    client_with_db,
)
from tests.helper_scripts.helper_functions import (
    get_boolean_dictionary,
    create_test_user_api,
    create_api_key,
    give_user_admin_role,
    check_response_status,
    create_test_user_setup,
)


def test_data_sources_get(
    client_with_db, connection_with_test_data: psycopg2.extensions.connection
):
    """
    Test that GET call to /data-sources endpoint retrieves data sources and correctly identifies specific sources by name
    """
    inserted_data_sources_found = get_boolean_dictionary(
        ("Source 1", "Source 2", "Source 3")
    )
    tus = create_test_user_setup(client_with_db)
    response = client_with_db.get(
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


def test_data_sources_post(
    client_with_db, dev_db_connection: psycopg2.extensions.connection
):
    """
    Test that POST call to /data-sources endpoint successfully creates a new data source with a unique name and verifies its existence in the database
    """

    tus = create_test_user_setup(client_with_db)
    give_user_admin_role(dev_db_connection, tus.user_info)

    name = str(uuid.uuid4())
    response = client_with_db.post(
        "/data-sources",
        json={"name": name},
        headers=tus.authorization_header,
    )
    check_response_status(response, HTTPStatus.OK.value)
    cursor = dev_db_connection.cursor()
    cursor.execute(
        """
    SELECT * from data_sources WHERE name=%s
    """,
        (name,),
    )
    rows = cursor.fetchall()
    assert (len(rows)) == 1
