"""Integration tests for /agencies endpoint"""

import time
from datetime import datetime, timezone, timedelta

from database_client.db_client_dataclasses import WhereMapping
from database_client.enums import SortOrder, ApprovalStatus
from database_client.models import Agency
from middleware.enums import JurisdictionType, AgencyType
from middleware.schema_and_dto_logic.primary_resource_schemas.agencies_advanced_schemas import (
    AgencyInfoPutSchema,
)
from middleware.schema_and_dto_logic.common_response_schemas import (
    MessageSchema,
)
from resources.endpoint_schema_config import SchemaConfigs

from tests.helper_scripts.common_test_data import get_test_name
from tests.helper_scripts.complex_test_data_creation_functions import (
    get_sample_agency_post_parameters,
)
from tests.helper_scripts.helper_classes.SchemaTestDataGenerator import (
    generate_test_data_from_schema,
)
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)
from tests.helper_scripts.constants import AGENCIES_BASE_ENDPOINT

from tests.helper_scripts.common_asserts import (
    assert_expected_get_many_result,
    assert_contains_key_value_pairs,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request

from tests.conftest import test_data_creator_flask, monkeysession


def test_agencies_get(test_data_creator_flask: TestDataCreatorFlask):
    """
    Test that GET call to /agencies endpoint properly retrieves a nonzero amount of data
    """
    tdc = test_data_creator_flask
    tdc.agency()
    tdc.agency()
    tdc.agency(jurisdiction_type=JurisdictionType.FEDERAL)
    tus = tdc.standard_user()

    # Check basic data retrieval
    response_json = tdc.request_validator.get_agency(
        headers=tus.api_authorization_header,
        sort_by="name",
        sort_order=SortOrder.ASCENDING,
    )

    assert_expected_get_many_result(
        response_json=response_json,
        expected_non_null_columns=["id"],
    )
    data_asc = response_json["data"]

    # Test pagination functionality
    response_json_2 = tdc.request_validator.get_agency(
        headers=tus.api_authorization_header,
        sort_by="name",
        sort_order=SortOrder.ASCENDING,
        page=2,
    )

    assert response_json != response_json_2

    # Test sort functionality
    response_json = tdc.request_validator.get_agency(
        headers=tus.api_authorization_header,
        sort_by="name",
        sort_order=SortOrder.DESCENDING,
    )

    assert_expected_get_many_result(
        response_json=response_json,
        expected_non_null_columns=["id"],
    )
    data_desc = response_json["data"]

    assert data_asc != data_desc
    assert data_asc[0]["name"] < data_desc[0]["name"]

    assert data_asc[0]["name"] == data_asc[0]["submitted_name"]

    # Test limit functionality
    response_json = tdc.request_validator.get_agency(
        headers=tus.api_authorization_header,
        sort_by="name",
        sort_order=SortOrder.ASCENDING,
        limit=1,
    )

    assert_expected_get_many_result(
        response_json=response_json,
        expected_non_null_columns=["id"],
    )
    assert len(response_json["data"]) == 1


def test_agencies_get_approval_filter(test_data_creator_flask: TestDataCreatorFlask):
    """
    Test that GET call to /agencies endpoint properly retrieves a nonzero amount of data
    """
    # Delete all agencies
    tdc = test_data_creator_flask
    tdc.clear_test_data()

    # Create two agencies with approved status
    tdc.agency()
    tdc.agency()

    # Create one agency with pending status
    tdc.agency(approval_status=ApprovalStatus.PENDING)

    # Get all agencies
    response_json = tdc.request_validator.get_agency(
        headers=tdc.get_admin_tus().jwt_authorization_header,
    )

    # Check that all agencies are retrieved
    assert len(response_json["data"]) == 3

    # Get all approved agencies
    response_json = tdc.request_validator.get_agency(
        headers=tdc.get_admin_tus().jwt_authorization_header,
        approval_status=ApprovalStatus.APPROVED,
    )

    # Check that only two agencies are retrieved
    assert len(response_json["data"]) == 2

    # Get all pending agencies
    response_json = tdc.request_validator.get_agency(
        headers=tdc.get_admin_tus().jwt_authorization_header,
        approval_status=ApprovalStatus.PENDING,
    )

    # Check that only one agency is retrieved
    assert len(response_json["data"]) == 1


def test_agencies_get_by_id(test_data_creator_flask: TestDataCreatorFlask):
    """
    Test that GET call to /agencies/<id> endpoint properly retrieves the correct data
    """
    tdc = test_data_creator_flask

    location_id_1 = tdc.locality()
    location_id_2 = tdc.locality()

    # Add data via db client
    agency_id = tdc.agency(
        location_ids=[location_id_1, location_id_2],
    ).id

    # link agency id to data source
    cds = tdc.data_source()
    tdc.link_data_source_to_agency(data_source_id=cds.id, agency_id=agency_id)

    response_json = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="get",
        endpoint=AGENCIES_BASE_ENDPOINT + f"/{agency_id}",
        headers=tdc.get_admin_tus().jwt_authorization_header,
        expected_schema=SchemaConfigs.AGENCIES_BY_ID_GET.value.primary_output_schema,
    )

    data = response_json["data"]
    assert data["name"] == data["submitted_name"]
    assert data["id"] == int(agency_id)
    assert data["data_sources"][0]["id"] == int(cds.id)

    assert data["locations"][0]["location_id"] == int(location_id_1)
    assert data["locations"][1]["location_id"] == int(location_id_2)


def test_agencies_post(test_data_creator_flask: TestDataCreatorFlask):
    tdc = test_data_creator_flask
    tdc.clear_test_data()

    start_of_test_datetime = datetime.now(timezone.utc)
    # Test once with an existing locality, and once with a new locality

    tus_admin = tdc.get_admin_tus()

    def run_post(
        json: dict,
    ):
        return run_and_validate_request(
            flask_client=tdc.flask_client,
            http_method="post",
            endpoint=AGENCIES_BASE_ENDPOINT,
            headers=tus_admin.jwt_authorization_header,
            json=json,
            expected_schema=SchemaConfigs.AGENCIES_POST.value.primary_output_schema,
        )

    def run_get(
        id_: str,
    ):
        return run_and_validate_request(
            flask_client=tdc.flask_client,
            http_method="get",
            endpoint=f"{AGENCIES_BASE_ENDPOINT}/{id_}",
            headers=tus_admin.jwt_authorization_header,
        )

    # Test with a new locality
    data_to_post = tdc.get_sample_agency_post_parameters(
        name=get_test_name(),
        jurisdiction_type=JurisdictionType.LOCAL,
        locality_name=get_test_name(),
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
            **data_to_post["agency_info"],
        },
    )
    # Check user id is correct
    agencies = tdc.db_client.get_all(Agency)
    assert len(agencies) == 1
    assert agencies[0]["creator_user_id"] == tus_admin.user_info.user_id

    # Test with a new locality
    data_to_post = test_data_creator_flask.get_sample_agency_post_parameters(
        name=get_test_name(),
        jurisdiction_type=JurisdictionType.LOCAL,
        locality_name="Capitola",
    )
    json_data = run_post(data_to_post)

    id_ = json_data["id"]

    json_data = run_get(id_)

    assert_contains_key_value_pairs(
        dict_to_check=json_data["data"],
        key_value_pairs={
            "name": data_to_post["agency_info"]["name"],
        },
    )


def test_agencies_put(test_data_creator_flask: TestDataCreatorFlask):
    tdc = test_data_creator_flask

    data_to_post = tdc.get_sample_agency_post_parameters(
        name=get_test_name(),
        jurisdiction_type=JurisdictionType.LOCAL,
        locality_name=get_test_name(),
    )

    admin_tus = tdc.get_admin_tus()

    json_data = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="post",
        endpoint=AGENCIES_BASE_ENDPOINT,
        headers=admin_tus.jwt_authorization_header,
        json=data_to_post,
    )

    agency_id = json_data["id"]

    # Add sleep to allow update time to be distinct from creation time
    time.sleep(1)

    BY_ID_ENDPOINT = f"{AGENCIES_BASE_ENDPOINT}/{agency_id}"

    agency_info = generate_test_data_from_schema(
        schema=AgencyInfoPutSchema(),
        override={
            "jurisdiction_type": JurisdictionType.FEDERAL.value,
        },
    )

    json_data = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="put",
        endpoint=BY_ID_ENDPOINT,
        headers=admin_tus.jwt_authorization_header,
        json={"agency_info": agency_info},
        expected_schema=SchemaConfigs.AGENCIES_BY_ID_PUT.value.primary_output_schema,
    )

    json_data = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="get",
        endpoint=BY_ID_ENDPOINT,
        headers=admin_tus.api_authorization_header,
    )

    assert_contains_key_value_pairs(
        dict_to_check=json_data["data"],
        key_value_pairs=agency_info,
    )

    agency_created = json_data["data"]["agency_created"]
    last_modified = json_data["data"]["airtable_agency_last_modified"]
    assert datetime.fromisoformat(agency_created) < datetime.fromisoformat(
        last_modified
    )


def test_agencies_delete(test_data_creator_flask: TestDataCreatorFlask):
    tdc = test_data_creator_flask
    admin_tus = tdc.get_admin_tus()

    json_data = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="post",
        endpoint=AGENCIES_BASE_ENDPOINT,
        headers=admin_tus.jwt_authorization_header,
        json={
            "agency_info": {
                "name": get_test_name(),
                "jurisdiction_type": JurisdictionType.FEDERAL.value,
                "agency_type": AgencyType.COURT.value,
            }
        },
    )

    agency_id = json_data["id"]

    run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="delete",
        endpoint=f"{AGENCIES_BASE_ENDPOINT}/{agency_id}",
        headers=admin_tus.jwt_authorization_header,
        expected_schema=MessageSchema,
    )

    results = tdc.db_client._select_from_relation(
        relation_name="agencies",
        columns=["name"],
        where_mappings=[WhereMapping(column="id", value=int(agency_id))],
    )

    assert len(results) == 0


def test_agencies_locations(test_data_creator_flask: TestDataCreatorFlask):
    tdc = test_data_creator_flask
    # Create agency
    agency_id = tdc.agency().id

    location_id = tdc.locality()

    # Add location
    tdc.request_validator.add_location_to_agency(
        headers=tdc.get_admin_tus().jwt_authorization_header,
        agency_id=agency_id,
        location_id=location_id,
    )

    # Get agency and confirm presence
    result = tdc.request_validator.get_agency_by_id(
        headers=tdc.get_admin_tus().api_authorization_header,
        id=agency_id,
    )

    assert len(result["data"]["locations"]) == 2

    # Remove location
    tdc.request_validator.remove_location_from_agency(
        headers=tdc.get_admin_tus().jwt_authorization_header,
        agency_id=agency_id,
        location_id=location_id,
    )

    # Get agency and confirm absence
    result = tdc.request_validator.get_agency_by_id(
        headers=tdc.get_admin_tus().api_authorization_header,
        id=agency_id,
    )

    assert len(result["data"]["locations"]) == 1
