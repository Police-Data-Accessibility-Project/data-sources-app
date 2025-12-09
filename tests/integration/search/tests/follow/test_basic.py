from http import HTTPStatus
from typing import Optional

from marshmallow import Schema

from db.enums import LocationType
from db.helpers_.result_formatting import get_display_name
from endpoints.schema_config.instantiations.search.follow.delete import (
    SearchFollowDeleteEndpointSchemaConfig,
)
from endpoints.instantiations.search.follow.get.schema_config import (
    SearchFollowGetEndpointSchemaConfig,
)
from middleware.enums import RecordTypesEnum
from tests.helpers.constants import SEARCH_FOLLOW_BASE_ENDPOINT
from tests.helpers.helper_classes.TestUserSetup import TestUserSetup
from tests.helpers.helper_functions_simple import add_query_params
from tests.helpers.run_and_validate_request import (
    http_methods,
    run_and_validate_request,
)
from tests.integration.search.constants import TEST_STATE, TEST_COUNTY, TEST_LOCALITY
from tests.integration.search.search_test_setup import SearchTestSetup
from utilities.enums import RecordCategoryEnum


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
                    RecordCategoryEnum.POLICE.value: [
                        RecordTypesEnum.ACCIDENT_REPORTS.value,
                        RecordTypesEnum.ARREST_RECORDS.value,
                        RecordTypesEnum.CALLS_FOR_SERVICE.value,
                        RecordTypesEnum.CAR_GPS.value,
                        RecordTypesEnum.CITATIONS.value,
                        RecordTypesEnum.DISPATCH_LOGS.value,
                        RecordTypesEnum.DISPATCH_RECORDINGS.value,
                        RecordTypesEnum.FIELD_CONTACTS.value,
                        RecordTypesEnum.INCIDENT_REPORTS.value,
                        RecordTypesEnum.MISC_POLICE_ACTIVITY.value,
                        RecordTypesEnum.OFFICER_INVOLVED_SHOOTINGS.value,
                        RecordTypesEnum.STOPS.value,
                        RecordTypesEnum.SURVEYS.value,
                        RecordTypesEnum.USE_OF_FORCE_REPORTS.value,
                        RecordTypesEnum.VEHICLE_PURSUITS.value,
                    ],
                    RecordCategoryEnum.JAIL.value: [
                        RecordTypesEnum.BOOKING_REPORTS.value,
                        RecordTypesEnum.COURT_CASES.value,
                        RecordTypesEnum.INCARCERATION_RECORDS.value,
                    ],
                    RecordCategoryEnum.OFFICERS.value: [
                        RecordTypesEnum.COMPLAINTS_MISCONDUCT.value,
                        RecordTypesEnum.DAILY_ACTIVITY_LOGS.value,
                        RecordTypesEnum.TRAINING_HIRING_INFO.value,
                        RecordTypesEnum.PERSONNEL_RECORDS.value,
                    ],
                    RecordCategoryEnum.AGENCIES.value: [
                        RecordTypesEnum.ANNUAL_MONTHLY_REPORTS.value,
                        RecordTypesEnum.BUDGETS_FINANCES.value,
                        RecordTypesEnum.CONTACT_INFO_AGENCY_META.value,
                        RecordTypesEnum.GEOGRAPHIC.value,
                        RecordTypesEnum.LIST_OF_DATA_SOURCES.value,
                        RecordTypesEnum.POLICIES_CONTRACTS.value,
                    ],
                    RecordCategoryEnum.RESOURCE.value: [
                        RecordTypesEnum.CRIME_MAPS_REPORTS.value,
                        RecordTypesEnum.CRIME_STATISTICS.value,
                        RecordTypesEnum.MEDIA_BULLETINS.value,
                        RecordTypesEnum.RECORDS_REQUEST_INFO.value,
                        RecordTypesEnum.RESOURCES.value,
                        RecordTypesEnum.SEX_OFFENDER_REGISTRY.value,
                        RecordTypesEnum.WANTED_PERSONS.value,
                    ],
                    RecordCategoryEnum.OTHER.value: [
                        RecordTypesEnum.OTHER.value,
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
            **location_to_follow,
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
