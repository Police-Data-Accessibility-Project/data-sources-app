import pytest
from unittest.mock import patch

from middleware.webhook_logic import post_to_webhook
from middleware.webhook_logic import send_password_reset_link


@pytest.fixture
def mock_env_variable():
    with patch("middleware.webhook_logic.get_env_variable") as mock_get_env_variable:
        yield mock_get_env_variable


@pytest.fixture
def mock_requests_post():
    with patch("middleware.webhook_logic.requests.post") as mock_post:
        yield mock_post


def test_post_to_webhook(mock_env_variable, mock_requests_post):
    mock_env_variable.side_effect = [
        "https://base_app.com",
        "https://example.com/webhook",
    ]
    data = '{"key": "value"}'
    post_to_webhook(data)

    assert mock_env_variable.call_count == 2
    mock_env_variable.assert_any_call("VITE_VUE_APP_BASE_URL")
    mock_env_variable.assert_any_call("WEBHOOK_URL")
    mock_requests_post.assert_called_once_with(
        url="https://example.com/webhook",
        data="(https://base_app.com) " + data,
        headers={"Content-Type": "application/json"},
        timeout=5,
    )


def test_send_password_reset_link(mock_env_variable, mock_requests_post):
    email = "test_email@test.com"
    token = "test_token"
    send_password_reset_link(email, token)

    assert mock_env_variable.call_count == 2
    mock_env_variable.assert_any_call("MAILGUN_KEY")
    mock_env_variable.assert_any_call("VITE_VUE_APP_BASE_URL")
    mock_requests_post.assert_called_once()
