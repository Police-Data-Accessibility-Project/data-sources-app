from http import HTTPStatus
from unittest.mock import MagicMock

from tests.fixtures import client_with_mock_db, bypass_jwt_required
from tests.helper_scripts.common_test_data import TEST_RESPONSE
from tests.helper_scripts.helper_functions import check_response_status


def post_login_request(client_with_mock_db, ip_address="127.0.0.1"):
    return client_with_mock_db.client.post(
        "/login",
        environ_base={"REMOTE_ADDR": ip_address},
        json={"email": "test_email", "password": "test_password"},
    )

def post_refresh_session_request(client_with_mock_db, ip_address="127.0.0.1"):
    return client_with_mock_db.client.post(
        "/refresh-session",
        environ_base={"REMOTE_ADDR": ip_address},
        json={"refresh_token": "test_refresh_token"},
    )

def test_rate_limiter_explicit_limit(client_with_mock_db, monkeypatch):
    """
    Test the rate limiter's explicit limit decorator using the login endpoint,
    which is rate limited at 5 requests per minute
    :param client_with_mock_db:
    :param monkeypatch:
    :return:
    """

    monkeypatch.setattr(
        f"resources.Login.try_logging_in", MagicMock(return_value=TEST_RESPONSE)
    )

    for i in range(5):
        response = post_login_request(client_with_mock_db)
        check_response_status(response, TEST_RESPONSE.status_code)

    response = post_login_request(client_with_mock_db)
    assert "5 per 1 minute" in response.json["message"]

    # Test that a different IP address still works
    response = post_login_request(client_with_mock_db, ip_address="237.84.2.178")
    check_response_status(response, TEST_RESPONSE.status_code)

def test_rate_limiter_default_limit(client_with_mock_db, monkeypatch, bypass_jwt_required):
    """
    Test the rate limiter's default limit decorator using the refresh-session endpoint
    which is not explicitly rate-limited and thus should default to
    50 per hour
    :param client_with_mock_db:
    :param monkeypatch:
    :return:
    """

    monkeypatch.setattr(
        f"resources.RefreshSession.refresh_session", MagicMock(return_value=TEST_RESPONSE)
    )

    for i in range(100):
        response = post_refresh_session_request(client_with_mock_db)
        check_response_status(response, TEST_RESPONSE.status_code)

    response = post_refresh_session_request(client_with_mock_db)
    check_response_status(response, HTTPStatus.TOO_MANY_REQUESTS)
    assert response.json["message"] == "100 per 1 hour"

    # Test that a different IP address still works
    response = post_refresh_session_request(client_with_mock_db, ip_address="237.84.2.178")
    check_response_status(response, TEST_RESPONSE.status_code)
