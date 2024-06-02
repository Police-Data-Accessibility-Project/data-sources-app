import unittest.mock
from collections import namedtuple

import pytest
from flask import Flask

from resources.SearchTokens import SearchTokens


class MockPsycopgConnection:
    def cursor(self):
        return MockCursor()

    def commit(self):
        pass

    def rollback(self):
        pass


class MockCursor:
    def execute(self, query, params=None):
        pass

    def fetchall(self):
        pass


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config.update({"TESTING": True})
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mock_psycopg_connection():
    return MockPsycopgConnection()


@pytest.fixture
def search_tokens(mock_psycopg_connection):
    return SearchTokens(psycopg2_connection=mock_psycopg_connection)


@pytest.fixture
def mock_dependencies(mocker):
    mocks = {
        "insert_access_token": mocker.patch(
            "resources.SearchTokens.insert_access_token", return_value=None
        ),
        "quick-search": mocker.patch(
            "resources.SearchTokens.quick_search_query_wrapper",
            return_value={"result": "quick_search"},
        ),
        "data-sources": mocker.patch(
            "resources.SearchTokens.get_approved_data_sources_wrapper",
            return_value={"result": "data_sources"},
        ),
        "data-sources-by-id": mocker.patch(
            "resources.SearchTokens.data_source_by_id_wrapper",
            return_value={"result": "data_source_by_id"},
        ),
        "data-sources-map": mocker.patch(
            "resources.SearchTokens.get_data_sources_for_map_wrapper",
            return_value={"result": "data_sources_map"},
        ),
    }
    return mocks


def perform_test_search_tokens_endpoint(
    search_tokens,
    mocker,
    app,
    endpoint,
    expected_response,
    params=None,
    mocked_dependencies: dict[str, unittest.mock.MagicMock] = None,
):
    mock_insert_access_token = mocker.patch(
        "resources.SearchTokens.insert_access_token"
    )
    url = generate_url(endpoint, params)

    with app.test_request_context(url):
        response = search_tokens.get()
        assert (
            response == expected_response
        ), f"{endpoint} endpoint should call {expected_response}, got {response}"
        mock_insert_access_token.assert_called_once()
        if endpoint in mocked_dependencies:
            # Check parameters properly called
            mock_dependency = mocked_dependencies[endpoint]
            call_args = tuple(params.values()) if params else ()
            mock_dependency.assert_called_with(
                *call_args, search_tokens.psycopg2_connection
            ), f"{mock_dependency._mock_name or 'mock'} was not called with the expected parameters"


def generate_url(endpoint, params):
    url = f"/?endpoint={endpoint}"
    if params:
        url += "".join([f"&{key}={value}" for key, value in params.items()])
    return url


TestCase = namedtuple("TestCase", ["endpoint", "expected_response", "params"])

test_cases = [
    TestCase(
        "quick-search", {"result": "quick_search"}, {"arg1": "test1", "arg2": "test2"}
    ),
    TestCase("data-sources", {"result": "data_sources"}, None),
    TestCase("data-sources-by-id", {"result": "data_source_by_id"}, {"arg1": "1"}),
    TestCase("data-sources-map", {"result": "data_sources_map"}, None),
]


@pytest.mark.parametrize("test_case", test_cases)
def test_endpoints(search_tokens, mocker, app, test_case, mock_dependencies):
    """
    Perform test for endpoints, ensuring each provided endpoint calls
    the appropriate wrapper function with the appropriate arguments

    :param search_tokens: The search tokens to be used for the test.
    :param mocker: The mocker object.
    :param app: The application object.
    :param test_case: The test case object.
    :return: None
    """
    perform_test_search_tokens_endpoint(
        search_tokens,
        mocker,
        app,
        test_case.endpoint,
        test_case.expected_response,
        test_case.params,
        mock_dependencies,
    )


def test_search_tokens_unknown_endpoint(app, mocker, search_tokens):
    url = generate_url("test_endpoint", {"test_param": "test_value"})
    with app.test_request_context(url):
        response = search_tokens.get()
        assert response.status_code == 500
        assert response.json == {"message": "Unknown endpoint: test_endpoint"}


def test_search_tokens_get_exception(app, mocker, search_tokens):
    mocker.patch(
        "resources.SearchTokens.insert_access_token",
        side_effect=Exception("Test exception"),
    )

    url = generate_url("test_endpoint", {"test_param": "test_value"})
    with app.test_request_context(url):
        response = search_tokens.get()
        assert response.status_code == 500
        assert response.json == {"message": "Test exception"}
