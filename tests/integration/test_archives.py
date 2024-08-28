"""Integration tests for /archives endpoint"""

import datetime
from http import HTTPStatus
import json

import psycopg

from database_client.database_client import DatabaseClient
from middleware.enums import PermissionsEnum
from tests.fixtures import (
    dev_db_connection,
    flask_client_with_db,
    dev_db_client,
    test_user_admin,
)
from tests.helper_scripts.helper_functions import (
    create_test_user_api,
    create_api_key,
    insert_test_data_source,
    create_test_user_setup,
    create_test_user_setup_db_client,
    run_and_validate_request,
)
from tests.helper_scripts.common_test_functions import check_response_status

ENDPOINT = "/api/archives"


def test_archives_get(flask_client_with_db, dev_db_client: DatabaseClient):
    """
    Test that GET call to /archives endpoint successfully retrieves a non-zero amount of data
    """
    tus = create_test_user_setup_db_client(
        dev_db_client,
    )
    response_json = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint=ENDPOINT,
        headers=tus.api_authorization_header,
    )

    assert len(response_json) > 0, "Endpoint should return more than 0 results"
    assert response_json[0]["id"] is not None


def test_archives_put(
    flask_client_with_db, dev_db_client: DatabaseClient, test_user_admin
):
    """
    Test that PUT call to /archives endpoint successfully updates the data source with last_cached and broken_source_url_as_of fields
    """
    data_source_id = insert_test_data_source(dev_db_client)
    last_cached = datetime.datetime(year=2020, month=3, day=4)
    broken_as_of = datetime.date(year=1993, month=11, day=13)
    test_user_admin.jwt_authorization_header["Content-Type"] = "application/json"
    run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="put",
        endpoint=ENDPOINT,
        headers=test_user_admin.jwt_authorization_header,
        json=json.dumps(
            {
                "id": data_source_id,
                "last_cached": str(last_cached),
                "broken_source_url_as_of": str(broken_as_of),
            }
        ),
    )

    row = dev_db_client.execute_raw_sql(
        query="""
        SELECT last_cached, broken_source_url_as_of 
        FROM data_sources 
        INNER JOIN data_sources_archive_info ON data_sources.airtable_uid = data_sources_archive_info.airtable_uid 
        WHERE data_sources.airtable_uid = %s
        """,
        vars=(data_source_id,),
    )
    assert row[0]["last_cached"] == last_cached
    assert row[0]["broken_source_url_as_of"] == broken_as_of
