from http import HTTPStatus
from typing import Optional

from marshmallow import Schema

from resources.endpoint_schema_config import SchemaConfigs
from tests.helper_scripts.constants import SEARCH_FOLLOW_BASE_ENDPOINT
from tests.helper_scripts.helper_classes.TestUserSetup import TestUserSetup
from tests.helper_scripts.helper_functions import (
    create_test_user_setup, add_query_params,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request, http_methods
from tests.helper_scripts.simple_result_validators import check_response_status
from tests.conftest import flask_client_with_db, bypass_api_key_required
from conftest import test_data_creator_flask, monkeysession


def test_search_get(flask_client_with_db, bypass_api_key_required):
    tus = create_test_user_setup(flask_client_with_db)

    data = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint="/search/search-location-and-record-type?state=Pennsylvania&county=Allegheny&locality=Pittsburgh&record_categories=Police%20%26%20Public%20Interactions",
        headers=tus.api_authorization_header,
    )

    jurisdictions = ["federal", "state", "county", "locality"]

    assert list(data.keys()) == ["count", "data"]
    assert list(data["data"].keys()).sort() == jurisdictions.sort()
    assert data["count"] > 0

    jurisdiction_count = 0
    for jurisdiction in jurisdictions:
        assert list(data["data"][jurisdiction].keys()) == ["count", "results"]
        jurisdiction_count += data["data"][jurisdiction]["count"]
        if data["data"][jurisdiction]["count"] > 0:
            assert (
                list(data["data"][jurisdiction]["results"][0].keys()).sort()
                == [
                    "agency_name",
                    "agency_supplied",
                    "coverage_end",
                    "coverage_start",
                    "data_source_name",
                    "description",
                    "jurisdiction_type",
                    "record_format",
                    "id",
                    "municipality",
                    "record_type",
                    "state",
                    "url",
                ].sort()
            )

    assert jurisdiction_count == data["count"]

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

    def call_follow_post(
        tus: TestUserSetup,
        endpoint: str = url_for_following,
        expected_json_content: Optional[dict] = None,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
    ):
        return call_search_endpoint(
            tus=tus,
            http_method="post",
            endpoint=endpoint,
            expected_json_content=expected_json_content,
            expected_response_status=expected_response_status,
            expected_schema=SchemaConfigs.SEARCH_FOLLOW_POST.value.output_schema,
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
            expected_schema=SchemaConfigs.SEARCH_FOLLOW_DELETE.value.output_schema,
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
            expected_schema=SchemaConfigs.SEARCH_FOLLOW_GET.value.output_schema,
        )

    no_results_json = {
        "data": [],
        "metadata": {"count": 0},
        "message": "Followed searches found."
    }


    # User should check current follows and find none
    call_follow_get(
        tus=tus_1,
        expected_json_content=no_results_json,
    )

    # User should try to follow a nonexistent location and be denied
    nonexistent_location = {
        "state": "Pennsylvania",
        "county": "Allegheny",
        "locality": "Purtsburgh",
    }
    url_for_failed_follow = add_query_params(
        SEARCH_FOLLOW_BASE_ENDPOINT, nonexistent_location
    )
    call_follow_post(
        tus=tus_1,
        endpoint=url_for_failed_follow,
        expected_response_status=HTTPStatus.BAD_REQUEST,
        expected_json_content={"message": "Location not found."},
    )

    # User should try to follow an extant location and be granted
    call_follow_post(
        tus=tus_1,
        endpoint=url_for_following,
        expected_json_content={
            "message": "Location followed."
        }
    )

    # If the user tries to follow the same location again, it should fail

    call_follow_post(
        tus=tus_1,
        endpoint=url_for_following,
        expected_json_content={
            "message": "Location already followed."
        }
    )

    # User should check current follows and find only the one they just followed
    call_follow_get(
        tus=tus_1,
        expected_json_content={
            "metadata": {"count": 1},
            "data": [location_to_follow],
            "message": "Followed searches found.",
        }
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
        expected_json_content={
            "message": "Followed search deleted."
        }
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
        expected_json_content={
            "message": "Location not followed."
        }
    )
