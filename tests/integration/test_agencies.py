"""Integration tests for /agencies endpoint"""

import uuid
from collections import namedtuple
from dataclasses import dataclass
from http import HTTPStatus
import psycopg
import pytest

from database_client.constants import PAGE_SIZE
from database_client.database_client import DatabaseClient
from middleware.enums import PermissionsEnum

from tests.fixtures import (
    dev_db_connection,
    flask_client_with_db,
    dev_db_client,
    integration_test_admin_setup,
)
from tests.helper_scripts.constants import AGENCIES_BASE_ENDPOINT
from tests.helper_scripts.helper_functions import (
    create_test_user_setup_db_client,
    create_test_user_setup,
)
from tests.helper_scripts.common_test_functions import (
    assert_expected_get_many_result,
    call_and_validate_get_by_id_endpoint, )
from tests.helper_scripts.run_and_validate_request import run_and_validate_request
from tests.helper_scripts.simple_result_validators import check_response_status
from tests.helper_scripts.helper_classes.IntegrationTestSetup import IntegrationTestSetup


@dataclass
class AgenciesTestSetup(IntegrationTestSetup):
    submitted_name: str = str(uuid.uuid4())


@pytest.fixture
def ts(integration_test_admin_setup: IntegrationTestSetup):
    tas = integration_test_admin_setup
    return AgenciesTestSetup(
        flask_client=tas.flask_client,
        db_client=tas.db_client,
        tus=tas.tus,
    )


def test_agencies_get(flask_client_with_db, dev_db_client: DatabaseClient):
    """
    Test that GET call to /agencies endpoint properly retrieves a nonzero amount of data
    """
    tus = create_test_user_setup_db_client(dev_db_client)

    response_json = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint=AGENCIES_BASE_ENDPOINT + "?page=2",
        headers=tus.api_authorization_header,
    )

    assert_expected_get_many_result(
        response_json=response_json,
        expected_non_null_columns=["airtable_uid"],
    )


def test_agencies_get_by_id(ts: AgenciesTestSetup):
    # Add data via db client
    airtable_uid = uuid.uuid4().hex
    ts.db_client._create_entry_in_table(
        table_name="agencies",
        column_value_mappings={"submitted_name": ts.submitted_name, "airtable_uid": airtable_uid},
    )

    call_and_validate_get_by_id_endpoint(
        its=ts,
        id_name=airtable_uid,
        base_endpoint=AGENCIES_BASE_ENDPOINT,
        expected_value_key="submitted_name",
        expected_value=ts.submitted_name,
    )


def test_agencies_post(ts: AgenciesTestSetup):

    json_data = run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="post",
        endpoint=AGENCIES_BASE_ENDPOINT,
        headers=ts.tus.jwt_authorization_header,
        json={
            "entry_data": {
                "submitted_name": ts.submitted_name,
                "airtable_uid": uuid.uuid4().hex,
            }
        },
    )

    results = ts.db_client._select_from_single_relation(
        relation_name="agencies",
        columns=["submitted_name"],
        where_mappings={"airtable_uid": json_data["id"]},
    )

    assert len(results) == 1

    assert results[0]["submitted_name"] == ts.submitted_name


def test_agencies_put(ts: AgenciesTestSetup):

    json_data = run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="post",
        endpoint=AGENCIES_BASE_ENDPOINT,
        headers=ts.tus.jwt_authorization_header,
        json={
            "entry_data": {
                "submitted_name": ts.submitted_name,
                "airtable_uid": uuid.uuid4().hex,
            }
        },
    )

    agency_id = json_data["id"]

    new_submitted_name = str(uuid.uuid4())

    json_data = run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="put",
        endpoint=f"{AGENCIES_BASE_ENDPOINT}/{agency_id}",
        headers=ts.tus.jwt_authorization_header,
        json={"entry_data": {"submitted_name": new_submitted_name}},
    )

    results = ts.db_client._select_from_single_relation(
        relation_name="agencies",
        columns=["submitted_name"],
        where_mappings={"airtable_uid": agency_id},
    )

    assert len(results) == 1

    assert results[0]["submitted_name"] == new_submitted_name


def test_agencies_delete(ts: AgenciesTestSetup):

    json_data = run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="post",
        endpoint=AGENCIES_BASE_ENDPOINT,
        headers=ts.tus.jwt_authorization_header,
        json={
            "entry_data": {
                "submitted_name": ts.submitted_name,
                "airtable_uid": uuid.uuid4().hex,
            }
        },
    )

    agency_id = json_data["id"]

    run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="delete",
        endpoint=f"{AGENCIES_BASE_ENDPOINT}/{agency_id}",
        headers=ts.tus.jwt_authorization_header,
    )

    results = ts.db_client._select_from_single_relation(
        relation_name="agencies",
        columns=["submitted_name"],
        where_mappings={"airtable_uid": agency_id},
    )

    assert len(results) == 0
