"""
Tests the check_api_key function in middleware.py
Though `check_api_key` is middleware, its underlying logic is complex enough
to warrant its own integration test for all possible outcomes.

Particularly given other integration tests for endpoints which utilize
decorators that call `check_api_key` do not currently
test the different possible outcomes of `check_api_key`
"""

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest

from middleware.security import check_api_key, INVALID_API_KEY_MESSAGE
from tests.helper_scripts.common_mocks_and_patches import (
    patch_request_headers,
    patch_abort,
)
from tests.conftest import dev_db_connection, db_cursor, live_database_client
from tests.helper_scripts.helper_functions import create_test_user_setup_db_client


@pytest.fixture
def mock_abort(monkeypatch) -> MagicMock:
    return patch_abort(monkeypatch, path="middleware.security")


PATCH_REQUESTS_ROOT = "middleware.access_logic"


def test_check_api_key_happy_path(monkeypatch, live_database_client):
    """
    In Happy path, the api key is valid, and check_api_key runs without error
    :param monkeypatch:
    :param live_database_client:
    :return:
    """

    tus = create_test_user_setup_db_client(live_database_client)

    patch_request_headers(
        monkeypatch,
        path=PATCH_REQUESTS_ROOT,
        request_headers=tus.api_authorization_header,
    )

    check_api_key()


@pytest.mark.parametrize(
    "request_headers",
    [
        None,
        {"Authorization": "Basic"},
        {"Authorization": "BasicAPIKEY"},
        {"Authorization": "Bearer api_key"},
        {"Authrztn": "Basic api_key"},
    ],
)
def test_check_api_key_valid_authorization_header(
    monkeypatch, mock_abort, request_headers
):
    """
    Test various scenarios where an Invalid API Key response is expected
    :param monkeypatch:
    :param mock_abort:
    :param request_headers:
    :return:
    """
    patch_request_headers(
        monkeypatch,
        path=PATCH_REQUESTS_ROOT,
        request_headers=request_headers,
    )

    check_api_key()
    mock_abort.assert_called_once_with(
        code=HTTPStatus.UNAUTHORIZED, message=INVALID_API_KEY_MESSAGE
    )


def test_check_api_key_api_key_not_associated_with_user(monkeypatch, mock_abort):

    patch_request_headers(
        monkeypatch,
        path=PATCH_REQUESTS_ROOT,
        request_headers={"Authorization": "Basic invalid_api_key"},
    )

    check_api_key()
    mock_abort.assert_called_once_with(HTTPStatus.UNAUTHORIZED, "Invalid API Key")
