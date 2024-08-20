"""Integration tests for /data-sources endpoint"""

from http import HTTPStatus
import uuid

import psycopg
from psycopg.extras import DictRow

from database_client.database_client import DatabaseClient
from middleware.enums import PermissionsEnum
from tests.fixtures import (
    connection_with_test_data,
    dev_db_connection,
    flask_client_with_db,
    db_client_with_test_data,
    test_user_admin,
)
from tests.helper_scripts.helper_functions import (
    get_boolean_dictionary,
    create_test_user_api,
    create_api_key,
    give_user_admin_role,
    check_response_status,
    create_test_user_setup,
    create_test_user_setup_db_client,
    run_and_validate_request,
    search_with_boolean_dictionary,
)

ENDPOINT = "/api/data-sources"


def test_data_sources_get(
    flask_client_with_db, connection_with_test_data: psycopg.extensions.connection
):
    """
    Test that GET call to /data-sources endpoint retrieves data sources and correctly identifies specific sources by name
    """
    inserted_data_sources_found = get_boolean_dictionary(
        ("Source 1", "Source 2", "Source 3")
    )
    tus = create_test_user_setup(flask_client_with_db)
    response_json = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint=ENDPOINT,
        headers=tus.api_authorization_header,
    )
    data = response_json["data"]
    search_with_boolean_dictionary(
        data=data,
        boolean_dictionary=inserted_data_sources_found,
        key_to_search_on="name",
    )
    assert inserted_data_sources_found["Source 1"]
    assert not inserted_data_sources_found["Source 2"]
    assert not inserted_data_sources_found["Source 3"]


def test_data_sources_post(
    flask_client_with_db,
    db_client_with_test_data: DatabaseClient,
    test_user_admin,
):
    """
    Test that POST call to /data-sources endpoint successfully creates a new data source with a unique name and verifies its existence in the database
    """

    name = str(uuid.uuid4())
    run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="post",
        endpoint=ENDPOINT,
        headers=test_user_admin.jwt_authorization_header,
        json={"name": name},
    )
    rows = db_client_with_test_data.execute_raw_sql(
        query="""
        SELECT * from data_sources WHERE name=%s
        """,
        vars=(name,),
    )
    len(rows) == 1
