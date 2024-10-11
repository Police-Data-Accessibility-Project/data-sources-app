"""
This module tests resources following a common format.
"""

import json
from unittest.mock import MagicMock

import pytest

from resources.ApiKey import API_KEY_ROUTE
from tests.conftest import (
    client_with_mock_db,
    bypass_api_key_required,
    bypass_permissions_required,
    bypass_jwt_required,
    bypass_authentication_required,
)
from http import HTTPStatus

from tests.helper_scripts.DynamicMagicMock import DynamicMagicMock
from tests.helper_scripts.constants import TEST_RESPONSE, GITHUB_DATA_REQUESTS_ISSUES_ENDPOINT
from tests.helper_scripts.helper_functions import (
    check_is_test_response,
    add_query_params,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request


class DataSourcesMocks(DynamicMagicMock):
    request: MagicMock
    data: MagicMock


MOCK_EMAIL_PASSWORD = {
    "email": "test_email",
    "password": "test_password",
}
TEST_ID = -1


@pytest.mark.parametrize(
    "endpoint, http_method, route_to_patch, json_data",
    (
        (
            f"/data-sources/{TEST_ID}",
            "GET",
            "DataSources.data_source_by_id_wrapper",
            {},
        ),
        (
            f"/data-sources/{TEST_ID}",
            "PUT",
            "DataSources.update_data_source_wrapper",
            {"entry_data": {}},
        ),
        (
            f"/data-sources/{TEST_ID}",
            "DELETE",
            "DataSources.delete_data_source_wrapper",
            {},
        ),
        (
            "/data-sources",
            "POST",
            "DataSources.add_new_data_source_wrapper",
            {"entry_data": {
                "submitted_name": "test_name",
                "description": "test_description",
                "airtable_uid": "test_airtable_uid",
                "approval_status": "approved",
            }},
        ),
        (
            "/data-sources?page=1&approval_status=approved",
            "GET",
            "DataSources.get_data_sources_wrapper",
            {},
        ),
        (
            "/data-requests/test_id/related-sources",
            "GET",
            "DataRequests.get_data_request_related_sources",
            {},
        ),
        # This endpoint no longer works because of the other data source endpoint
        # It is interpreted as another data source id
        # But we have not yet decided whether to modify or remove it entirely
        # (
        #     "/data-sources/data-sources-map",
        #     "GET",
        #     "DataSources.get_data_sources_for_map_wrapper",
        #     {},
        # ),
        (
            "/archives",
            "PUT",
            "Archives.update_archives_data",
            json.dumps(
                {
                    "id": TEST_ID,
                    "last_cached": "2019-01-01",
                    "broken_source_url_as_of": "2019-02-02",
                }
            ),
        ),
        ("/archives", "GET", "Archives.archives_get_query", {}),
        (
            f"auth{API_KEY_ROUTE}",
            "POST",
            "ApiKey.get_api_key_for_user",
            MOCK_EMAIL_PASSWORD,
        ),
        ("auth/callback", "GET", "Callback.callback_outer_wrapper", {}),
        ("/login", "POST", "Login.try_logging_in", MOCK_EMAIL_PASSWORD),
        ("/refresh-session", "POST", "RefreshSession.refresh_session", {}),
        (
            "/request-reset-password",
            "POST",
            "RequestResetPassword.request_reset_password",
            {},
        ),
        (
            "/reset-password",
            "POST",
            "ResetPassword.reset_password",
            {
                "email": "test_email",
                "token": "test_token",
                "password": "test_password",
            },
        ),
        (
            "/reset-token-validation",
            "POST",
            "ResetTokenValidation.reset_token_validation",
            {
                "token": "test_token",
            },
        ),
        (
            "/typeahead/locations?query=test_query",
            "GET",
            "TypeaheadSuggestions.get_typeahead_results",
            {},
        ),
        (
            "typeahead/locations?query=test_query",
            "GET",
            "TypeaheadSuggestions.get_typeahead_results",
            {},
        ),
        (
            "/auth/permissions?user_email=test-user",
            "GET",
            "Permissions.manage_user_permissions",
            {},
        ),
        (
            "/auth/permissions?user_email=test-user",
            "PUT",
            "Permissions.update_permissions_wrapper",
            {
                "action": "test-action",
                "permission": "test-permission",
            },
        ),
        (
            "/data-requests",
            "POST",
            "DataRequests.create_data_request_wrapper",
            {"entry_data": {"sample_column": "sample_value"}},
        ),
        (
            "/data-requests",
            "GET",
            "DataRequests.get_data_requests_wrapper",
            {},
        ),
        (
            f"/data-requests/{TEST_ID}",
            "GET",
            "DataRequests.get_data_request_by_id_wrapper",
            {},
        ),
        (
            f"/data-requests/{TEST_ID}",
            "PUT",
            "DataRequests.update_data_request_wrapper",
            {"entry_data": {"sample_column": "sample_value"}},
        ),
        (
            f"/data-requests/{TEST_ID}",
            "DELETE",
            "DataRequests.delete_data_request_wrapper",
            {},
        ),
        # Below should not be used until: https://github.com/Police-Data-Accessibility-Project/data-sources-app/issues/458
        # (
        #     "/homepage-search-cache",
        #     "POST",
        #     "HomepageSearchCache.update_search_cache",
        #     {
        #         "search_results": ["test_result_1", "test_result_2"],
        #         "agency_airtable_uid": "test_airtable_uid",
        #     },
        # ),
        # (
        #     "/homepage-search-cache",
        #     "GET",
        #     "HomepageSearchCache.get_agencies_without_homepage_urls",
        #     {},
        # ),
        (
            "/agencies?page=1",
            "GET",
            "Agencies.get_agencies",
            {},
        ),
        (
            f"/agencies/{TEST_ID}",
            "GET",
            "Agencies.get_agency_by_id",
            {},
        ),
        (
            f"/agencies/{TEST_ID}",
            "PUT",
            "Agencies.update_agency",
            {
                "entry_data": {
                    "submitted_name": "test_agency_name",
                    "airtable_uid": "test_airtable_uid",
                }
            },
        ),
        (f"/agencies/{TEST_ID}", "DELETE", "Agencies.delete_agency", {}),
        (
            add_query_params(
                url="/check/unique-url", params={"url": "https://www.test-url.com"}
            ),
            "GET",
            "UniqueURLChecker.unique_url_checker_wrapper",
            {},
        ),
        (
            GITHUB_DATA_REQUESTS_ISSUES_ENDPOINT.format(
                data_request_id="123"
            ),
            "POST",
            "GithubDataRequestsIssues.add_data_request_as_github_issue",
            {},
        )
    ),
)
def test_common_format_resources(
    endpoint,
    http_method,
    route_to_patch,
    json_data,
    client_with_mock_db,
    monkeypatch,
    bypass_api_key_required,
    bypass_permissions_required,
    bypass_jwt_required,
    bypass_authentication_required,
):

    monkeypatch.setattr(
        f"resources.{route_to_patch}", MagicMock(return_value=TEST_RESPONSE)
    )

    run_and_validate_request(
        flask_client=client_with_mock_db.client,
        http_method=http_method,
        endpoint=endpoint,
        json=json_data,
        expected_json_content=TEST_RESPONSE.response,
        expected_response_status=TEST_RESPONSE.status_code,
    )
