import csv
from dataclasses import dataclass
from http import HTTPStatus
from typing import Optional

import pytest
from marshmallow import Schema

from database_client.enums import LocationType, ApprovalStatus
from middleware.enums import OutputFormatEnum, JurisdictionSimplified
from middleware.util import bytes_to_text_iter, read_from_csv, get_enum_values
from resources.endpoint_schema_config import SchemaConfigs
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)
from tests.helper_scripts.constants import (
    SEARCH_FOLLOW_BASE_ENDPOINT,
    USER_PROFILE_RECENT_SEARCHES_ENDPOINT,
)
from tests.helper_scripts.helper_classes.TestUserSetup import TestUserSetup
from tests.helper_scripts.helper_functions_simple import add_query_params
from tests.helper_scripts.run_and_validate_request import (
    run_and_validate_request,
    http_methods,
)
from conftest import test_data_creator_flask, monkeysession
from utilities.enums import RecordCategories

ENDPOINT_SEARCH_LOCATION_AND_RECORD_TYPE = "/search/search-location-and-record-type"


TEST_STATE = "Pennsylvania"
TEST_COUNTY = "Allegheny"
TEST_LOCALITY = "Pittsburgh"


@dataclass
class SearchTestSetup:
    tdc: TestDataCreatorFlask
    location_id: int
    tus: TestUserSetup


@pytest.fixture
def search_test_setup(test_data_creator_flask: TestDataCreatorFlask):
    tdc = test_data_creator_flask
    try:
        tdc.locality(TEST_LOCALITY)
    except Exception:
        pass
    return SearchTestSetup(
        tdc=tdc,
        location_id=tdc.db_client.get_location_id(
            where_mappings={
                "state_name": TEST_STATE,
                "county_name": TEST_COUNTY,
                "locality_name": TEST_LOCALITY,
            }
        ),
        tus=tdc.standard_user(),
    )


def test_search_get(search_test_setup: SearchTestSetup):
    sts = search_test_setup
    tdc = sts.tdc
    tus = sts.tus
    tdcdb = tdc.tdcdb

    tdcdb.link_data_source_to_agency(
        data_source_id=tdcdb.data_source(
            approval_status=ApprovalStatus.APPROVED,
            record_type_id=1,
            source_url="http://example.com",
            agency_supplied=True,
        ).id,
        agency_id=tdcdb.agency(location_id=sts.location_id).id,
    )

    def search(record_format: Optional[OutputFormatEnum] = OutputFormatEnum.JSON):
        return tdc.request_validator.search(
            headers=tus.api_authorization_header,
            location_id=sts.location_id,
            record_categories=[RecordCategories.POLICE],
            format=record_format,
        )

    json_data = search()

    jurisdictions = get_enum_values(JurisdictionSimplified)

    assert json_data["count"] > 0

    jurisdiction_count = 0
    for jurisdiction in jurisdictions:
        jurisdiction_count += json_data["data"][jurisdiction]["count"]

    assert jurisdiction_count == json_data["count"]

    # Check that search shows up in user's recent searches
    data = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="get",
        endpoint=USER_PROFILE_RECENT_SEARCHES_ENDPOINT,
        headers=tus.jwt_authorization_header,
        expected_schema=SchemaConfigs.USER_PROFILE_RECENT_SEARCHES.value.primary_output_schema,
    )

    assert data["metadata"]["count"] == 1

    assert data["data"][0] == {
        "location_id": sts.location_id,
        "state_name": TEST_STATE,
        "county_name": TEST_COUNTY,
        "locality_name": TEST_LOCALITY,
        "location_type": LocationType.LOCALITY.value,
        "record_categories": [RecordCategories.POLICE.value],
    }

    csv_data = search(record_format=OutputFormatEnum.CSV)

    results = read_from_csv(csv_data)

    assert len(results) == json_data["count"]

    # Flatten json data for comparison
    flat_json_data = []
    for jurisdiction in jurisdictions:
        if json_data["data"][jurisdiction]["count"] == 0:
            continue
        for result in json_data["data"][jurisdiction]["results"]:
            flat_json_data.append(result)

    # Sort both the flat json data and the csv results for comparison
    # Due to differences in how CSV and JSON results are formatted, compare only ids
    json_ids = sorted([result["id"] for result in flat_json_data])
    csv_ids = sorted(
        [int(result["id"]) for result in results]
    )  # CSV ids are formatted as strings

    assert json_ids == csv_ids


def test_search_get_record_categories_all(
    search_test_setup: SearchTestSetup,
):
    """
    All record categories can be provided in one of two ways:
    By explicitly passing an "ALL" value in the `record_categories` parameter
    Or by providing every non-ALL value in the `record_categories` parameter
    """
    sts = search_test_setup
    tdc = sts.tdc
    tus = sts.tus

    tdcdb = tdc.tdcdb

    tdcdb.link_data_source_to_agency(
        data_source_id=tdcdb.data_source(
            approval_status=ApprovalStatus.APPROVED,
            record_type_id=1,
            source_url="http://example.com",
            agency_supplied=True,
        ).id,
        agency_id=tdcdb.agency(location_id=sts.location_id).id,
    )

    def run_search(record_categories: list[RecordCategories]) -> dict:
        return tdc.request_validator.search(
            headers=tus.api_authorization_header,
            location_id=sts.location_id,
            record_categories=record_categories if len(record_categories) > 0 else None,
        )

    data_all_explicit = run_search(record_categories=[RecordCategories.ALL])
    assert data_all_explicit["count"] > 0

    # Check that the count is the same as if every record type is provided
    data_all_implicit = run_search(
        record_categories=[rc for rc in RecordCategories if rc != RecordCategories.ALL]
    )
    assert data_all_implicit["count"] > 0
    assert data_all_implicit["count"] == data_all_explicit["count"]

    # Check that the count is the same if no record type is provided
    data_empty = run_search(record_categories=[])
    assert data_empty["count"] > 0
    assert data_empty["count"] == data_all_explicit["count"]


def test_search_follow(search_test_setup: SearchTestSetup):
    sts = search_test_setup
    tdc = sts.tdc
    # Create standard user
    tus_1 = sts.tus

    location_to_follow = {
        "location_id": sts.location_id,
    }
    url_for_following = add_query_params(
        SEARCH_FOLLOW_BASE_ENDPOINT, location_to_follow
    )

    def call_search_endpoint(
        tus: TestUserSetup,
        http_method: http_methods,
        endpoint: str = SEARCH_FOLLOW_BASE_ENDPOINT,
        expected_json_content: Optional[dict] = None,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_schema: Optional[Schema] = None,
    ):
        return run_and_validate_request(
            flask_client=tdc.flask_client,
            http_method=http_method,
            endpoint=endpoint,
            headers=tus.jwt_authorization_header,
            expected_json_content=expected_json_content,
            expected_response_status=expected_response_status,
            expected_schema=expected_schema,
        )

    def call_follow_delete(
        tus: TestUserSetup,
        endpoint: str = url_for_following,
        expected_json_content: Optional[dict] = None,
    ):
        return call_search_endpoint(
            tus=tus,
            http_method="delete",
            endpoint=endpoint,
            expected_json_content=expected_json_content,
            expected_schema=SchemaConfigs.SEARCH_FOLLOW_DELETE.value.primary_output_schema,
        )

    def call_follow_get(
        tus: TestUserSetup,
        expected_json_content: Optional[dict] = None,
    ):
        return call_search_endpoint(
            tus=tus,
            http_method="get",
            endpoint=SEARCH_FOLLOW_BASE_ENDPOINT,
            expected_json_content=expected_json_content,
            expected_schema=SchemaConfigs.SEARCH_FOLLOW_GET.value.primary_output_schema,
        )

    no_results_json = {
        "data": [],
        "metadata": {"count": 0},
        "message": "Followed searches found.",
    }

    # User should check current follows and find none
    call_follow_get(
        tus=tus_1,
        expected_json_content=no_results_json,
    )

    # User should try to follow a nonexistent location and be denied
    tdc.request_validator.follow_search(
        headers=tus_1.jwt_authorization_header,
        location_id=-1,
        expected_response_status=HTTPStatus.BAD_REQUEST,
        expected_json_content={"message": "Location for followed search not found."},
    )

    # User should try to follow an extant location and be granted
    def follow_extant_location(
        message: str = "Location followed.",
    ):
        tdc.request_validator.follow_search(
            headers=tus_1.jwt_authorization_header,
            expected_json_content={"message": message},
            **location_to_follow
        )

    follow_extant_location()

    # If the user tries to follow the same location again, it should fail
    follow_extant_location(message="Location already followed.")

    # User should check current follows and find only the one they just followed
    call_follow_get(
        tus=tus_1,
        expected_json_content={
            "metadata": {"count": 1},
            "data": [
                {
                    "state_name": TEST_STATE,
                    "county_name": TEST_COUNTY,
                    "locality_name": TEST_LOCALITY,
                    "location_id": sts.location_id,
                }
            ],
            "message": "Followed searches found.",
        },
    )

    # A separate user should check their current follows and find nothing

    tus_2 = tdc.standard_user()
    call_follow_get(
        tus=tus_2,
        expected_json_content=no_results_json,
    )

    # The original user should now try to unfollow the location and succeed
    call_follow_delete(
        tus=tus_1,
        endpoint=url_for_following,
        expected_json_content={"message": "Location for followed search deleted."},
    )

    # The original user, on checking their current follows, should now find no locations
    call_follow_get(
        tus=tus_1,
        expected_json_content=no_results_json,
    )

    # If the original user tries to unfollow the location again, it should fail
    call_follow_delete(
        tus=tus_1,
        endpoint=url_for_following,
        expected_json_content={"message": "Location not followed."},
    )
