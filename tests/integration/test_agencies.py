"""Integration tests for /agencies endpoint"""

import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
import pytest

from database_client.database_client import DatabaseClient
from database_client.db_client_dataclasses import WhereMapping
from middleware.enums import JurisdictionType
from middleware.schema_and_dto_logic.primary_resource_schemas.agencies_schemas import (
    AgenciesGetByIDResponseSchema,
    AgenciesGetManyResponseSchema,
)
from middleware.schema_and_dto_logic.common_response_schemas import (
    MessageSchema,
    IDAndMessageSchema,
)
from resources.endpoint_schema_config import SchemaConfigs

from tests.conftest import (
    dev_db_client,
    flask_client_with_db,
    integration_test_admin_setup,
)
from tests.helper_scripts.common_test_data import get_sample_agency_post_parameters, TestDataCreatorFlask
from tests.helper_scripts.constants import AGENCIES_BASE_ENDPOINT
from tests.helper_scripts.helper_functions import (
    create_test_user_setup_db_client,
)
from tests.helper_scripts.common_test_functions import (
    assert_expected_get_many_result, assert_contains_key_value_pairs,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request
from tests.helper_scripts.helper_classes.IntegrationTestSetup import (
    IntegrationTestSetup,
)
from conftest import test_data_creator_flask, monkeysession


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


def test_agencies_get(test_data_creator_flask: TestDataCreatorFlask):
    """
    Test that GET call to /agencies endpoint properly retrieves a nonzero amount of data
    """
    tdc = test_data_creator_flask
    tus = tdc.standard_user()

    response_json = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="get",
        endpoint=AGENCIES_BASE_ENDPOINT + "?page=2",
        headers=tus.api_authorization_header,
        expected_schema=SchemaConfigs.AGENCIES_GET_MANY.value.primary_output_schema,
    )

    assert_expected_get_many_result(
        response_json=response_json,
        expected_non_null_columns=["id"],
    )


def test_agencies_get_by_id(ts: AgenciesTestSetup):
    # Add data via db client
    agency_id = ts.db_client._create_entry_in_table(
        table_name="agencies",
        column_value_mappings={
            "submitted_name": ts.submitted_name,
            "jurisdiction_type": JurisdictionType.FEDERAL.value,
        },
        column_to_return="id",
    )

    response_json = run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="get",
        endpoint=AGENCIES_BASE_ENDPOINT + f"/{agency_id}",
        headers=ts.tus.jwt_authorization_header,
        expected_schema=SchemaConfigs.AGENCIES_BY_ID_GET.value.primary_output_schema,
    )

    assert response_json["data"]["id"] == agency_id


def test_agencies_post(ts: AgenciesTestSetup):

    start_of_test_datetime = datetime.now(timezone.utc)
    # Test once with an existing locality, and once with a new locality

    def run_post(
        json: dict,
    ):
        return run_and_validate_request(
            flask_client=ts.flask_client,
            http_method="post",
            endpoint=AGENCIES_BASE_ENDPOINT,
            headers=ts.tus.jwt_authorization_header,
            json=json,
            expected_schema=SchemaConfigs.AGENCIES_POST.value.primary_output_schema,
        )

    def run_get(
        id_: str,
    ):
        return run_and_validate_request(
            flask_client=ts.flask_client,
            http_method="get",
            endpoint=f"{AGENCIES_BASE_ENDPOINT}/{id_}",
            headers=ts.tus.jwt_authorization_header,
        )

    # Test with a new locality
    data_to_post = get_sample_agency_post_parameters(
        submitted_name=ts.submitted_name,
        jurisdiction_type=JurisdictionType.LOCAL,
        locality_name=uuid.uuid4().hex,
    )
    json_data = run_post(data_to_post)
    id_ = json_data["id"]

    json_data = run_get(id_)

    agency_created = json_data["data"]["agency_created"]
    last_modified = json_data["data"]["airtable_agency_last_modified"]
    assert (
        agency_created == last_modified
    ), "Agency created should be equal to last modified"
    assert (
        # Within one minute to account for minor database/app discrepancies
        datetime.fromisoformat(agency_created) + timedelta(minutes=1)
        > start_of_test_datetime
    ), "Agency created should be after start of test"

    assert_contains_key_value_pairs(
        dict_to_check=json_data["data"],
        key_value_pairs={
            "submitted_name": ts.submitted_name,
            "state_iso": "CA",
            "county_name": "Santa Cruz",
            "locality_name": data_to_post["location_info"]["locality_name"],
        }
    )

    # Test with a new locality
    data_to_post = get_sample_agency_post_parameters(
        submitted_name=uuid.uuid4().hex,
        jurisdiction_type=JurisdictionType.LOCAL,
        locality_name="Capitola",
    )
    json_data = run_post(data_to_post)

    id_ = json_data["id"]

    json_data = run_get(id_)

    assert_contains_key_value_pairs(
        dict_to_check=json_data["data"],
        key_value_pairs={
            "submitted_name": data_to_post["agency_info"]["submitted_name"],
            "state_iso": "CA",
            "county_name": "Santa Cruz",
            "locality_name": data_to_post["location_info"]["locality_name"],
        }
    )


def test_agencies_put(ts: AgenciesTestSetup):
    data_to_post = get_sample_agency_post_parameters(
        submitted_name=ts.submitted_name,
        jurisdiction_type=JurisdictionType.LOCAL,
        locality_name=uuid.uuid4().hex,
    )

    json_data = run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="post",
        endpoint=AGENCIES_BASE_ENDPOINT,
        headers=ts.tus.jwt_authorization_header,
        json=data_to_post,
    )

    agency_id = json_data["id"]

    new_submitted_name = str(uuid.uuid4())

    # Add sleep to allow update time to be distinct from creation time
    time.sleep(1)

    BY_ID_ENDPOINT = f"{AGENCIES_BASE_ENDPOINT}/{agency_id}"

    json_data = run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="put",
        endpoint=BY_ID_ENDPOINT,
        headers=ts.tus.jwt_authorization_header,
        json={"agency_info": {"submitted_name": new_submitted_name}},
        expected_schema=SchemaConfigs.AGENCIES_BY_ID_PUT.value.primary_output_schema,
    )

    json_data = run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="get",
        endpoint=BY_ID_ENDPOINT,
        headers=ts.tus.api_authorization_header,
    )

    agency_created = json_data["data"]["agency_created"]
    last_modified = json_data["data"]["airtable_agency_last_modified"]
    assert datetime.fromisoformat(agency_created) < datetime.fromisoformat(
        last_modified
    )

    assert json_data["data"]["submitted_name"] == new_submitted_name


def test_agencies_delete(ts: AgenciesTestSetup):

    json_data = run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="post",
        endpoint=AGENCIES_BASE_ENDPOINT,
        headers=ts.tus.jwt_authorization_header,
        json={
            "agency_info": {
                "submitted_name": ts.submitted_name,
                "jurisdiction_type": JurisdictionType.FEDERAL.value,
            }
        },
    )

    agency_id = json_data["id"]

    run_and_validate_request(
        flask_client=ts.flask_client,
        http_method="delete",
        endpoint=f"{AGENCIES_BASE_ENDPOINT}/{agency_id}",
        headers=ts.tus.jwt_authorization_header,
        expected_schema=MessageSchema,
    )

    results = ts.db_client._select_from_relation(
        relation_name="agencies",
        columns=["submitted_name"],
        where_mappings=[WhereMapping(column="id", value=int(agency_id))],
    )

    assert len(results) == 0
