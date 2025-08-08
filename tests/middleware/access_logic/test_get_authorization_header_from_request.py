from middleware.security.access_logic import get_authorization_header_from_request
from tests.helpers.common_mocks_and_patches import patch_request_headers


def test_get_authorization_header_from_request_happy_path(monkeypatch):
    patch_request_headers(
        monkeypatch,
        path="middleware.security.access_logic",
        request_headers={"Authorization": "Basic api_key"},
    )
    assert "Basic api_key" == get_authorization_header_from_request()
