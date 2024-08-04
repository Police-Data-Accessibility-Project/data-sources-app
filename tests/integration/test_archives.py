"""Integration tests for /archives endpoint"""

import datetime
from http import HTTPStatus
import json

import psycopg2

from database_client.database_client import DatabaseClient
from tests.fixtures import dev_db_connection, client_with_db
from tests.helper_scripts.helper_functions import (
    create_test_user_api,
    create_api_key,
    insert_test_data_source,
    create_test_user_setup,
)


def test_archives_get(
    client_with_db, dev_db_connection: psycopg2.extensions.connection
):
    """
    Test that GET call to /archives endpoint successfully retrieves a non-zero amount of data
    """
    user_info = create_test_user_api(client_with_db)
    api_key = create_api_key(client_with_db, user_info)
    response = client_with_db.get(
        "/api/archives",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    assert (
        response.status_code == HTTPStatus.OK.value
    ), "Archives endpoint returned non-200"
    assert len(response.json) > 0, "Endpoint should return more than 0 results"
    assert response.json[0]["id"] is not None


def test_archives_put(
    client_with_db, dev_db_connection: psycopg2.extensions.connection
):
    """
    Test that PUT call to /archives endpoint successfully updates the data source with last_cached and broken_source_url_as_of fields
    """
    tus = create_test_user_setup(client_with_db)
    data_source_id = insert_test_data_source(dev_db_connection.cursor())
    last_cached = datetime.datetime(year=2020, month=3, day=4)
    broken_as_of = datetime.date(year=1993, month=11, day=13)
    tus.authorization_header["Content-Type"] = "application/json"
    response = client_with_db.put(
        "/archives",
        headers=tus.authorization_header,
        json=json.dumps(
            {
                "id": data_source_id,
                "last_cached": str(last_cached),
                "broken_source_url_as_of": str(broken_as_of),
            }
        ),
    )
    assert response.status_code == HTTPStatus.OK.value, "Endpoint returned non-200"

    cursor = dev_db_connection.cursor()
    cursor.execute(
        """
    SELECT last_cached, broken_source_url_as_of 
    FROM data_sources 
    INNER JOIN data_sources_archive_info ON data_sources.airtable_uid = data_sources_archive_info.airtable_uid 
    WHERE data_sources.airtable_uid = %s
    """,
        (data_source_id,),
    )
    row = cursor.fetchone()
    assert row[0] == last_cached
    assert row[1] == broken_as_of
