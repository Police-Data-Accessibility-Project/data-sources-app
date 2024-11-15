from http import HTTPStatus
from typing import Optional

from marshmallow import Schema

from resources.endpoint_schema_config import SchemaConfigs
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import TestDataCreatorFlask
from tests.helper_scripts.constants import (
    SEARCH_FOLLOW_BASE_ENDPOINT,
    USER_PROFILE_RECENT_SEARCHES_ENDPOINT,
)
from tests.helper_scripts.helper_classes.TestUserSetup import TestUserSetup
from tests.helper_scripts.helper_functions import (
    add_query_params,
)
from tests.helper_scripts.run_and_validate_request import (
    run_and_validate_request,
    http_methods,
)
from tests.conftest import flask_client_with_db, bypass_api_key_required
from conftest import test_data_creator_flask, monkeysession
from utilities.enums import RecordCategories

ENDPOINT_SEARCH_LOCATION_AND_RECORD_TYPE = "/search/search-location-and-record-type"


def test_search_get(
    test_data_creator_flask: TestDataCreatorFlask, bypass_api_key_required
):
    tdc = test_data_creator_flask
    tus = tdc.standard_user()

    data = tdc.request_validator.search(
        headers=tus.api_authorization_header,
        state="Pennsylvania",
        county="Allegheny",
        locality="Pittsburgh",
        record_categories=[RecordCategories.POLICE],
    )

    jurisdictions = ["federal", "state", "county", "locality"]

    assert data["count"] > 0

    jurisdiction_count = 0
    for jurisdiction in jurisdictions:
        jurisdiction_count += data["data"][jurisdiction]["count"]

    assert jurisdiction_count == data["count"]

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
        "state_iso": "PA",
        "county_name": "Allegheny",
        "locality_name": "Pittsburgh",
        "location_type": "Locality",
        "record_categories": ["Police & Public Interactions"],
    }


def test_search_get_record_categories_all(
    test_data_creator_flask: TestDataCreatorFlask, bypass_api_key_required
):
    """
    All record categories can be provided in one of two ways:
    By explicitly passing an "ALL" value in the `record_categories` parameter
    Or by providing every non-ALL value in the `record_categories` parameter
    """
    tdc = test_data_creator_flask
    tus = tdc.standard_user()

    def run_search(record_categories: list[RecordCategories]) -> dict:
        return tdc.request_validator.search(
            headers=tus.api_authorization_header,
            state="Pennsylvania",
            county="Allegheny",
            locality="Pittsburgh",
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


def test_search_follow(test_data_creator_flask):
    tdc = test_data_creator_flask

    # Create standard user
    tus_1 = tdc.standard_user()

    location_to_follow = {
        "state": "Pennsylvania",
        "county": "Allegheny",
        "locality": "Pittsburgh",
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
        state="Pennsylvania",
        county="Allegheny",
        locality="Purtsburgh",
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

    # If the user tries to follow the same location again, it should fail
    follow_extant_location(message="Location already followed.")

    # User should check current follows and find only the one they just followed
    call_follow_get(
        tus=tus_1,
        expected_json_content={
            "metadata": {"count": 1},
            "data": [location_to_follow],
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
        expected_json_content={"message": "Followed search deleted."},
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
