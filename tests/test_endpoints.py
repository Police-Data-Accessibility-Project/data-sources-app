"""
This module tests the functionality of all endpoints, ensuring that, as designed, they call (or don't call)
the appropriate methods in their supporting classes
"""

from collections import namedtuple
from http import HTTPStatus

import pytest
from unittest.mock import patch

from flask.testing import FlaskClient
from flask_restful import Resource

from resources.Agencies import AgenciesByPage, AgenciesPost, AgenciesById
from resources.ApiKey import ApiKey, API_KEY_ROUTE
from resources.Archives import Archives
from resources.Callback import Callback
from resources.CreateUserWithGithub import CreateUserWithGithub
from resources.DataRequests import DataRequests, DataRequestsById
from resources.DataSources import (
    DataSources,
    DataSourcesMap,
    DataSourceById,
    DataSourcesPost,
)
from resources.HomepageSearchCache import HomepageSearchCache
from resources.LinkToGithub import LinkToGithub
from resources.Login import Login
from resources.LoginWithGithub import LoginWithGithub
from resources.Permissions import Permissions
from resources.QuickSearch import QuickSearch
from resources.RefreshSession import RefreshSession
from resources.RequestResetPassword import RequestResetPassword
from resources.ResetPassword import ResetPassword
from resources.ResetTokenValidation import ResetTokenValidation
from resources.Search import Search
from resources.TypeaheadSuggestions import TypeaheadSuggestions
from resources.User import User
from tests.fixtures import client_with_mock_db, ClientWithMockDB

# Define constants for HTTP methods
GET = "get"
POST = "post"
PUT = "put"
DELETE = "delete"


def run_endpoint_tests(
    client: FlaskClient, endpoint: str, class_type: Resource, allowed_methods: list[str]
):
    methods = [GET, POST, PUT, DELETE]
    for method in methods:
        if method in allowed_methods:
            with patch.object(
                class_type, method, return_value="Mocked response"
            ) as mock_method:
                response = getattr(client, method)(endpoint)
                assert (
                    response.status_code == HTTPStatus.OK.value
                ), f"{method.upper()} {endpoint} failed with status code {response.status_code}, expected 200"
                mock_method.assert_called_once(), f"{method.upper()} {endpoint} should have called the {method} method on {class_type.__name__}"
        else:
            response = getattr(client, method)(endpoint)
            assert (
                response.status_code == HTTPStatus.METHOD_NOT_ALLOWED.value
            ), f"{method.upper()} {endpoint} failed with status code {response.status_code}, expected 405"


TestParameters = namedtuple("Resource", ["class_type", "endpoint", "allowed_methods"])
test_parameters = [
    TestParameters(User, "/user", [POST, PUT]),
    TestParameters(Login, "/login", [POST]),
    TestParameters(RefreshSession, "/refresh-session", [POST]),
    TestParameters(ApiKey, f"/auth{API_KEY_ROUTE}", [POST]),
    TestParameters(RequestResetPassword, "/request-reset-password", [POST]),
    TestParameters(ResetPassword, "/reset-password", [POST]),
    TestParameters(ResetTokenValidation, "/reset-token-validation", [POST]),
    TestParameters(QuickSearch, "/quick-search/<search>/<location>", [GET]),
    TestParameters(Archives, "/archives", [GET, PUT]),
    TestParameters(DataSources, "/data-sources/page/<page>", [GET]),
    TestParameters(DataSourcesPost, "/data-sources/", [POST]),
    TestParameters(DataSourcesMap, "/data-sources/data-sources-map", [GET]),
    TestParameters(DataSourceById, "/data-sources/id/<data_source_id>", [GET, PUT, DELETE]),
    TestParameters(AgenciesPost, "/agencies/", [POST]),
    TestParameters(AgenciesByPage, "/agencies/page/<page>", [GET]),
    TestParameters(AgenciesById, "/agencies/id/<agency_id>", [GET, PUT, DELETE]),
    TestParameters(Search, "/search/search-location-and-record-type", [GET]),
    TestParameters(TypeaheadSuggestions, "/search/typeahead-suggestions", [GET]),
    TestParameters(Callback, "auth/callback", [GET]),
    TestParameters(LinkToGithub, "auth/link-to-github", [POST]),
    TestParameters(LoginWithGithub, "auth/login-with-github", [POST]),
    TestParameters(CreateUserWithGithub, "auth/create-user-with-github", [POST]),
    TestParameters(Permissions, "auth/permissions", [GET, PUT]),
    TestParameters(DataRequests, "/data-requests/", [GET, POST]),
    TestParameters(
        DataRequestsById, "/data-requests/by-id/<data_request_id>", [GET, PUT, DELETE]
    ),
    TestParameters(HomepageSearchCache, "/homepage-search-cache", [GET, POST]),
]


@pytest.mark.parametrize("test_parameter", test_parameters)
def test_endpoints(client_with_mock_db: ClientWithMockDB, test_parameter) -> None:
    """
    Using the test_parameters list, this tests all endpoints to ensure that
    only the appropriate methods can be called from the endpoints
    :param client: the client fixture
    :param class_type:
    :param endpoint:
    :param allowed_methods:
    :return:
    """
    run_endpoint_tests(
        client_with_mock_db.client,
        test_parameter.endpoint,
        test_parameter.class_type,
        test_parameter.allowed_methods,
    )
