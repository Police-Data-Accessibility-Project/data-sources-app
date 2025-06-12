from http import HTTPStatus
from typing import Optional

from marshmallow import Schema

from db.enums import LocationType
from db.helpers_.result_formatting import get_display_name
from endpoints.schema_config.instantiations.search.follow.delete import (
    SearchFollowDeleteEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.search.follow.get import (
    SearchFollowGetEndpointSchemaConfig,
)
from middleware.enums import RecordTypes
from tests.helper_scripts.constants import SEARCH_FOLLOW_BASE_ENDPOINT
from tests.helper_scripts.helper_classes.TestUserSetup import TestUserSetup
from tests.helper_scripts.helper_functions_simple import add_query_params
from tests.helper_scripts.run_and_validate_request import (
    http_methods,
    run_and_validate_request,
)
from tests.integration.search.constants import TEST_STATE, TEST_COUNTY, TEST_LOCALITY
from tests.integration.search.search_test_setup import SearchTestSetup
from utilities.enums import RecordCategories


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
            expected_schema=SearchFollowDeleteEndpointSchemaConfig.primary_output_schema,
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
            expected_schema=SearchFollowGetEndpointSchemaConfig.primary_output_schema,
        )

    no_results_json = {
        "data": [],
        "metadata": {"count": 0},
        "message": "Followed searches found.",
    }

    results_json = {
        "metadata": {"count": 1},
        "data": [
            {
                "state_name": TEST_STATE,
                "county_name": TEST_COUNTY,
                "locality_name": TEST_LOCALITY,
                "display_name": get_display_name(
                    location_type=LocationType.LOCALITY,
                    state_name=TEST_STATE,
                    county_name=TEST_COUNTY,
                    locality_name=TEST_LOCALITY,
                ),
                "location_id": sts.location_id,
                "subscriptions_by_category": {
                    RecordCategories.POLICE.value: [
                        RecordTypes.ACCIDENT_REPORTS.value,
                        RecordTypes.ARREST_RECORDS.value,
                        RecordTypes.CALLS_FOR_SERVICE.value,
                        RecordTypes.CAR_GPS.value,
                        RecordTypes.CITATIONS.value,
                        RecordTypes.DISPATCH_LOGS.value,
                        RecordTypes.DISPATCH_RECORDINGS.value,
                        RecordTypes.FIELD_CONTACTS.value,
                        RecordTypes.INCIDENT_REPORTS.value,
                        RecordTypes.MISC_POLICE_ACTIVITY.value,
                        RecordTypes.OFFICER_INVOLVED_SHOOTINGS.value,
                        RecordTypes.STOPS.value,
                        RecordTypes.SURVEYS.value,
                        RecordTypes.USE_OF_FORCE_REPORTS.value,
                        RecordTypes.VEHICLE_PURSUITS.value,
                    ],
                    RecordCategories.JAIL.value: [
                        RecordTypes.BOOKING_REPORTS.value,
                        RecordTypes.COURT_CASES.value,
                        RecordTypes.INCARCERATION_RECORDS.value,
                    ],
                    RecordCategories.OFFICERS.value: [
                        RecordTypes.COMPLAINTS_MISCONDUCT.value,
                        RecordTypes.DAILY_ACTIVITY_LOGS.value,
                        RecordTypes.TRAINING_HIRING_INFO.value,
                        RecordTypes.PERSONNEL_RECORDS.value,
                    ],
                    RecordCategories.AGENCIES.value: [
                        RecordTypes.ANNUAL_MONTHLY_REPORTS.value,
                        RecordTypes.BUDGETS_FINANCES.value,
                        RecordTypes.CONTACT_INFO_AGENCY_META.value,
                        RecordTypes.GEOGRAPHIC.value,
                        RecordTypes.LIST_OF_DATA_SOURCES.value,
                        RecordTypes.POLICIES_CONTRACTS.value,
                    ],
                    RecordCategories.RESOURCE.value: [
                        RecordTypes.CRIME_MAPS_REPORTS.value,
                        RecordTypes.CRIME_STATISTICS.value,
                        RecordTypes.MEDIA_BULLETINS.value,
                        RecordTypes.RECORDS_REQUEST_INFO.value,
                        RecordTypes.RESOURCES.value,
                        RecordTypes.SEX_OFFENDER_REGISTRY.value,
                        RecordTypes.WANTED_PERSONS.value,
                    ],
                    RecordCategories.OTHER.value: [
                        RecordTypes.OTHER.value,
                    ],
                },
            }
        ],
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
        expected_json_content={"message": "Location not found."},
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

    # If the user tries to follow the same location again, it should return the same result
    follow_extant_location(message="Location followed.")

    # User should check current follows and find only the one they just followed
    call_follow_get(
        tus=tus_1,
        expected_json_content=results_json,
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
        expected_json_content={"message": "Unfollowed search."},
    )

    # The original user, on checking their current follows, should now find no locations
    call_follow_get(
        tus=tus_1,
        expected_json_content=no_results_json,
    )

    # If the original user tries to unfollow the location again, it should return the same message.
    call_follow_delete(
        tus=tus_1,
        endpoint=url_for_following,
        expected_json_content={"message": "Unfollowed search."},
    )
