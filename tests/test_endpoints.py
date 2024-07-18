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

from resources.Agencies import Agencies
from resources.ApiKey import ApiKey
from resources.Archives import Archives
from resources.DataSources import (
    DataSources,
    DataSourcesMap,
    DataSourcesNeedsIdentification,
    DataSourceById,
)
from resources.Login import Login
from resources.QuickSearch import QuickSearch
from resources.RefreshSession import RefreshSession
from resources.RequestResetPassword import RequestResetPassword
from resources.ResetPassword import ResetPassword
from resources.ResetTokenValidation import ResetTokenValidation
from resources.Search import Search
from resources.SearchTokens import SearchTokens
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
    TestParameters(ApiKey, "/api/api_key", [GET]),
    TestParameters(RequestResetPassword, "/request-reset-password", [POST]),
    TestParameters(ResetPassword, "/reset-password", [POST]),
    TestParameters(ResetTokenValidation, "/reset-token-validation", [POST]),
    TestParameters(QuickSearch, "/quick-search/<search>/<location>", [GET]),
    TestParameters(Archives, "/archives", [GET, PUT]),
    TestParameters(DataSources, "/data-sources", [GET, POST]),
    TestParameters(DataSourcesMap, "/data-sources-map", [GET]),
    TestParameters(
        DataSourcesNeedsIdentification, "/data-sources-needs-identification", [GET]
    ),
    TestParameters(DataSourceById, "/data-sources-by-id/<data_source_id>", [GET, PUT]),
    TestParameters(Agencies, "/agencies/<page>", [GET]),
    TestParameters(SearchTokens, "/search-tokens", [GET]),
    TestParameters(Search, "/search", [GET]),
    TestParameters(TypeaheadSuggestions, "/search/typeahead-suggestions", [GET]),
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
