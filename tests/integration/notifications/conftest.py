from unittest.mock import MagicMock

import pytest

PATCH_ROOT = "middleware.primary_resource_logic.notifications.notifications"


@pytest.fixture
def mock_format_and_send_notifications(monkeypatch):
    mock_format_and_send_notifications = MagicMock()
    monkeypatch.setattr(
        f"{PATCH_ROOT}.format_and_send_notifications",
        mock_format_and_send_notifications,
    )
    return mock_format_and_send_notifications
