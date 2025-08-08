from middleware.security.api_key.helpers import get_key_from_authorization_header


def test_get_api_key_from_authorization_header_happy_path(monkeypatch):
    assert "api_key" == get_key_from_authorization_header("Basic api_key")


