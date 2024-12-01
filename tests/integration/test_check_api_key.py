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

from middleware.exceptions import (
    InvalidAuthorizationHeaderException,
    InvalidAPIKeyException,
)
from middleware.primary_resource_logic.api_key_logic import (
    INVALID_API_KEY_MESSAGE,
    check_api_key,
)
from tests.helper_scripts.DynamicMagicMock import DynamicMagicMock
from tests.helper_scripts.common_mocks_and_patches import (
    patch_request_headers,
    patch_abort,
)
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)
from conftest import test_data_creator_flask, monkeysession


PATCH_API_KEY_ROOT = "middleware.primary_resource_logic.api_key_logic"


@pytest.fixture
def mock_abort(monkeypatch) -> MagicMock:
    return patch_abort(monkeypatch, path=PATCH_API_KEY_ROOT)


PATCH_REQUESTS_ROOT = "middleware.access_logic"


def test_check_api_key_happy_path(
    monkeypatch, test_data_creator_flask: TestDataCreatorFlask
):
    """
    In Happy path, the api key is valid, and check_api_key runs without error
    :param monkeypatch:
    :param live_database_client:
    :return:
    """
    tdc = test_data_creator_flask
    tus = tdc.standard_user()

    patch_request_headers(
        monkeypatch,
        path=PATCH_REQUESTS_ROOT,
        request_headers=tus.api_authorization_header,
    )

    check_api_key()


#
def test_check_api_key_api_key_not_associated_with_user(monkeypatch, mock_abort):

    patch_request_headers(
        monkeypatch,
        path=PATCH_REQUESTS_ROOT,
        request_headers={"Authorization": "Basic invalid_api_key"},
    )

    check_api_key()
    mock_abort.assert_called_once_with(HTTPStatus.UNAUTHORIZED, "Invalid API Key")


class CheckApiKeyMocks(DynamicMagicMock):
    get_db_client: MagicMock
    get_api_key_from_request_header: MagicMock
    check_api_key_associated_with_user: MagicMock
