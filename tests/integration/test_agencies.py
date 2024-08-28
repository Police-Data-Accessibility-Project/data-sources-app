"""Integration tests for /agencies endpoint"""

import uuid
from collections import namedtuple
from http import HTTPStatus
import psycopg
import pytest

from database_client.constants import PAGE_SIZE
from database_client.database_client import DatabaseClient

from tests.fixtures import dev_db_connection, flask_client_with_db, dev_db_client
from tests.helper_scripts.helper_functions import (
    create_test_user_setup_db_client,
    run_and_validate_request,
    create_test_user_setup,
)
from tests.helper_scripts.common_test_functions import (
    check_response_status,
    assert_expected_get_many_result,
)


AgenciesTestSetup = namedtuple(
    "TestSetup", ["flask_client", "db_client", "submitted_name", "tus"]
)


@pytest.fixture
def ts(flask_client_with_db, dev_db_client):
    return AgenciesTestSetup(
        flask_client=flask_client_with_db,
        db_client=dev_db_client,
        submitted_name=str(uuid.uuid4()),
        tus=create_test_user_setup(
            flask_client_with_db,
            permissions=[PermissionsEnum.DB_WRITE],
        ),
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

    assert_expected_get_many_result(
        response_json=response_json,
        expected_non_null_columns=["airtable_uid"],
    )


def test_agencies_post(ts: AgenciesTestSetup):

    json_data = run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="post",
        endpoint="/api/agencies/",
        headers=ts.tus.jwt_authorization_header,
        json={"entry_data": {"submitted_name": ts.submitted_name}},
    )
