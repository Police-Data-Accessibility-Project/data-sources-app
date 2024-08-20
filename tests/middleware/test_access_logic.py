from dataclasses import dataclass

import pytest

from middleware.access_logic import (
    get_authorization_header_from_request,
    InvalidAuthorizationHeaderException,
    get_api_key_from_authorization_header,
    InvalidAPIKeyException,
)
from tests.helper_scripts.common_mocks_and_patches import patch_request_headers


def test_get_authorization_header_from_request_happy_path(monkeypatch):
    patch_request_headers(
        monkeypatch,
        path="middleware.access_logic",
        request_headers={"Authorization": "Basic api_key"},
    )
    assert "Basic api_key" == get_authorization_header_from_request()


@pytest.mark.parametrize(
    "request_headers",
    [
        {},
        {"Authrztn": "Basic api_key"},
    ],
)
def test_get_authorization_header_from_request_invalid_authorization_header(
    monkeypatch, request_headers
):
    patch_request_headers(
        monkeypatch,
        path="middleware.access_logic",
        request_headers=request_headers,
    )
    with pytest.raises(InvalidAuthorizationHeaderException):
        get_authorization_header_from_request()


def test_get_api_key_from_authorization_header_happy_path(monkeypatch):
    assert "api_key" == get_api_key_from_authorization_header("Basic api_key")


@pytest.mark.parametrize(
    "authorization_header",
    [
        None,
        "Basic",
        "Bearer api_key",
    ],
)
def test_get_api_key_from_authorization_header_invalid_authorization_header(
    monkeypatch, authorization_header
):
    with pytest.raises(InvalidAPIKeyException):
        get_api_key_from_authorization_header(authorization_header)
