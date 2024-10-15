"""Integration tests for /archives endpoint"""

import datetime
from http import HTTPStatus
import json

import psycopg

from database_client.database_client import DatabaseClient
from middleware.enums import PermissionsEnum
from tests.conftest import dev_db_client, flask_client_with_db, test_user_admin
from tests.helper_scripts.common_test_data import TestDataCreatorFlask
from tests.helper_scripts.helper_functions import (
    create_test_user_api,
    create_api_key,
    insert_test_data_source,
    create_test_user_setup,
    create_test_user_setup_db_client,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request
from tests.helper_scripts.simple_result_validators import check_response_status
from conftest import test_data_creator_flask, monkeysession

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
    test_data_creator_flask: TestDataCreatorFlask,
):
    """
    Test that PUT call to /archives endpoint successfully updates the data source with last_cached and broken_source_url_as_of fields
    """
    tdc = test_data_creator_flask
    data_source_id = tdc.data_source().id
    last_cached = datetime.datetime(year=2020, month=3, day=4)
    broken_as_of = datetime.date(year=1993, month=11, day=13)
    test_user_admin = tdc.get_admin_tus()
    test_user_admin.jwt_authorization_header["Content-Type"] = "application/json"
    run_and_validate_request(
        flask_client=tdc.flask_client,
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

    row = tdc.db_client.execute_raw_sql(
        query="""
        SELECT last_cached, broken_source_url_as_of 
        FROM data_sources 
        INNER JOIN data_sources_archive_info ON data_sources.id = data_sources_archive_info.data_source_id 
        WHERE data_sources.id = %s
        """,
        vars=(int(data_source_id),),
    )
    assert row[0]["last_cached"] == last_cached
    assert row[0]["broken_source_url_as_of"] == broken_as_of
