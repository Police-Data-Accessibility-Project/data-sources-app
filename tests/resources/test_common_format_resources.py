"""
This module tests resources following a common format.
"""

import json
from unittest.mock import MagicMock

import pytest

from resources.ApiKey import API_KEY_ROUTE
from tests.fixtures import (
    client_with_mock_db,
    bypass_api_key_required,
    bypass_permissions_required,
    bypass_jwt_required,
    bypass_authentication_required
)
from http import HTTPStatus

from tests.helper_scripts.DynamicMagicMock import DynamicMagicMock
from tests.helper_scripts.common_test_data import TEST_RESPONSE
from tests.helper_scripts.helper_functions import (
    check_is_test_response,
)
from tests.helper_scripts.common_test_functions import run_and_validate_request


class DataSourcesMocks(DynamicMagicMock):
    request: MagicMock
    data: MagicMock


MOCK_EMAIL_PASSWORD = {
    "email": "test_email",
    "password": "test_password",
}


@pytest.mark.parametrize(
    "endpoint, http_method, route_to_patch, json_data",
    (
        (
            "/data-sources-by-id/test_id",
            "GET",
            "DataSources.data_source_by_id_wrapper",
            {},
        ),
        (
            "/data-sources-by-id/test_id",
            "PUT",
            "DataSources.update_data_source_wrapper",
            {},
        ),
        ("/data-sources", "POST", "DataSources.add_new_data_source_wrapper", {}),
        (
            "/data-sources-map",
            "GET",
            "DataSources.get_data_sources_for_map_wrapper",
            {},
        ),
        (
            "/archives",
            "PUT",
            "Archives.update_archives_data",
            json.dumps(
                {
                    "id": "test_id",
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
            "/search/typeahead-suggestions?query=test_query",
            "GET",
            "TypeaheadSuggestions.get_typeahead_suggestions_wrapper",
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
            "/data-requests/",
            "POST",
            "DataRequests.create_data_request_wrapper",
            {
                "entry_data": {
                    "sample_column": "sample_value"
                }
            },
        ),
        (
            "/data-requests/",
            "GET",
            "DataRequests.get_data_requests_wrapper",
            {},
        ),
        (
            "/data-requests/by-id/test_id",
            "GET",
            "DataRequests.get_data_request_by_id_wrapper",
            {},
        ),
        (
            "/data-requests/by-id/test_id",
            "PUT",
            "DataRequests.update_data_request_wrapper",
            {
                "entry_data": {
                    "sample_column": "sample_value"
                }
            },
        ),
        (
            "/data-requests/by-id/test_id",
            "DELETE",
            "DataRequests.delete_data_request_wrapper",
            {}
        ),
        (
            "/homepage-search-cache",
            "POST",
            "HomepageSearchCache.update_search_cache",
            {
                "search_results": ["test_result_1", "test_result_2"],
                "agency_airtable_uid": "test_airtable_uid"
            },
        ),
        (
            "/homepage-search-cache",
            "GET",
            "HomepageSearchCache.get_agencies_without_homepage_urls",
            {}
        ),
        (
            "/agencies/page/1",
            "GET",
            "Agencies.get_agencies",
            {},
        ),
        (
            "/agencies/",
            "POST",
            "Agencies.create_agency",
            {
                "entry_data":
                    {
                        "submitted_name": "test_agency_name",
                        "airtable_uid": "test_airtable_uid"
                    }
            },
        ),
        (
            "/agencies/id/test_id",
            "GET",
            "Agencies.get_agency_by_id",
            {},
        ),
        (
            "/agencies/id/test_id",
            "PUT",
            "Agencies.update_agency",
            {
                "entry_data":
                    {
                        "submitted_name": "test_agency_name",
                        "airtable_uid": "test_airtable_uid"
                    }
            },
        ),
        (
            "/agencies/id/test_id",
            "DELETE",
            "Agencies.delete_agency",
            {}
        ),

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
    bypass_authentication_required
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
