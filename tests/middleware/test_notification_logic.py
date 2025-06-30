import os
from unittest import mock

import pytest

from db.enums import EventType, EntityType
from db.dtos.event_batch import EventBatch
from db.dtos.event_info import EventInfo
from middleware.primary_resource_logic.notifications.notifications import (
    format_and_send_notifications,
)
from tests.helper_scripts.common_mocks_and_patches import patch_and_return_mock

PATCH_ROOT = "middleware.primary_resource_logic.notifications.notifications"


def remove_all_whitespaces(s: str):
    return "".join(s.split())


class SpaceAgnosticStringComparator:
    """
    Used to compare two strings without taking spaces into account
    """

    def __init__(self, s: str):
        self.s = s

    def __eq__(self, other: str):
        return remove_all_whitespaces(self.s) == remove_all_whitespaces(other)

    def __ne__(self, other: str):
        return remove_all_whitespaces(self.s) != remove_all_whitespaces(other)

    def __repr__(self):
        return self.s


@pytest.fixture
def mock_vite_vue_app_base_url(monkeypatch):
    """
    Mock the VITE_VUE_APP_BASE_URL environment variable
    to return a test url
    :param monkeypatch:
    :return:
    """
    with mock.patch.dict(os.environ, clear=True):
        envvars = {"VITE_VUE_APP_BASE_URL": "https://test.com"}
        for key, value in envvars.items():
            monkeypatch.setenv(key, value)

        yield


@pytest.fixture
def mock_send_via_mailgun(monkeypatch):
    """
    Mock the send_via_mailgun function
    :param monkeypatch:
    :return:
    """
    return patch_and_return_mock(f"{PATCH_ROOT}.send_via_mailgun", monkeypatch)


def test_format_and_send_notification_all_categories(
    mock_send_via_mailgun, mock_vite_vue_app_base_url
):
    test_event_batch = EventBatch(
        user_id=20,
        user_email="fancyfrank@frankfurters.com",
        events=[
            EventInfo(
                event_id=1,
                event_type=EventType.REQUEST_READY_TO_START,
                entity_id=39,
                entity_type=EntityType.DATA_REQUEST,
                entity_name="Test Data Request 1",
            ),
            EventInfo(
                event_id=2,
                event_type=EventType.REQUEST_COMPLETE,
                entity_id=45,
                entity_type=EntityType.DATA_REQUEST,
                entity_name="Test Data Request 2",
            ),
            EventInfo(
                event_id=3,
                event_type=EventType.DATA_SOURCE_APPROVED,
                entity_id=52,
                entity_type=EntityType.DATA_SOURCE,
                entity_name="Test Data Source 1",
            ),
            EventInfo(
                event_id=4,
                event_type=EventType.DATA_SOURCE_APPROVED,
                entity_id=79,
                entity_type=EntityType.DATA_SOURCE,
                entity_name="Test Data Source 2",
            ),
        ],
    )

    format_and_send_notifications(event_batch=test_event_batch)

    html_text = """<!DOCTYPE html>
<html>
  <head>
    <title>Notifications</title>
  </head>
  <body>
    <p>Greetings from the Police Data Access Point!</p>
    <p>There have been updates to locations you've followed since we last sent notifications.</p><br>
    <h1>New Data Sources</h1>
    <p>The following data sources were approved:</p>
    <div>
      <ul>
        <li>
          <a href="https://test.com/data-source/52">Test Data Source 1</a>
        </li>
        <li>
          <a href="https://test.com/data-source/79">Test Data Source 2</a>
        </li>
      </ul>
    </div><br>
    <h1>Data Request Completed</h1>
    <p>The following data request was completed:</p>
    <div>
      <ul>
        <li>
          <a href="https://test.com/data-request/45">Test Data Request 2</a>
        </li>
      </ul>
    </div><br>
    <h1>Data Request Started</h1>
    <p>The following data request was started:</p>
    <div>
      <ul>
        <li>
          <a href="https://test.com/data-request/39">Test Data Request 1</a>
        </li>
      </ul>
    </div><br>
    <p>Click 
      <a href="https://test.com/profile">here</a> to view and update your followed locations.
    </p>
  </body>
</html>"""

    base_text = """
    Greetings from the Police Data Access Point!
    
    There have been updates to locations you've followed since we last sent notifications.
        

New Data Sources
The following data sources were approved:
	- "Test Data Source 1" at https://test.com/data-source/52
	- "Test Data Source 2" at https://test.com/data-source/79


Data Request Completed
The following data request was completed:
	- "Test Data Request 2" at https://test.com/data-request/45


Data Request Started
The following data request was started:
	- "Test Data Request 1" at https://test.com/data-request/39

Click here to view and update your followed locations: https://test.com/profile"""

    mock_send_via_mailgun.assert_called_once_with(
        to_email=test_event_batch.user_email,
        subject="Updates to police data sources in locations you follow",
        text=SpaceAgnosticStringComparator(base_text),
        html=html_text,
    )


def test_format_and_send_notification_single_category(
    mock_send_via_mailgun, mock_vite_vue_app_base_url
):
    """
    Test that when a category is not included, the header doesn't appear
    :param monkeypatch:
    :return:
    """
    test_event_batch = EventBatch(
        user_id=20,
        user_email="fancyfrank@frankfurters.com",
        events=[
            EventInfo(
                event_id=1,
                event_type=EventType.REQUEST_COMPLETE,
                entity_id=22,
                entity_type=EntityType.DATA_REQUEST,
                entity_name="Test Data Request Alpha",
            ),
            EventInfo(
                event_id=2,
                event_type=EventType.REQUEST_COMPLETE,
                entity_id=91,
                entity_type=EntityType.DATA_REQUEST,
                entity_name="Test Data Request Omega",
            ),
        ],
    )

    format_and_send_notifications(event_batch=test_event_batch)

    html_text = """<!DOCTYPE html>
<html>
  <head>
    <title>Notifications</title>
  </head>
  <body>
    <p>Greetings from the Police Data Access Point!</p>
    <p>There have been updates to locations you've followed since we last sent notifications.</p><br>
    <h1>Data Requests Completed</h1>
    <p>The following data requests were completed:</p>
    <div>
      <ul>
        <li>
          <a href="https://test.com/data-request/22">Test Data Request Alpha</a>
        </li>
        <li>
          <a href="https://test.com/data-request/91">Test Data Request Omega</a>
        </li>
      </ul>
    </div><br>
    <p>Click 
      <a href="https://test.com/profile">here</a> to view and update your followed locations.
    </p>
  </body>
</html>"""

    base_text = """
Greetings from the Police Data Access Point!
    
There have been updates to locations you've followed since we last sent notifications.
        

    Data Requests Completed
The following data requests were completed:
	- "Test Data Request Alpha" at https://test.com/data-request/22
	- "Test Data Request Omega" at https://test.com/data-request/91

    Click here to view and update your followed locations: 
    https://test.com/profile
    
"""

    mock_send_via_mailgun.assert_called_once_with(
        to_email=test_event_batch.user_email,
        subject="Updates to police data sources in locations you follow",
        text=SpaceAgnosticStringComparator(base_text),
        html=SpaceAgnosticStringComparator(html_text),
    )


def test_format_and_send_notifications_error_no_events(
    mock_send_via_mailgun, mock_vite_vue_app_base_url
):
    """
    Test that an error is thrown when there are no events included in the batch
    :param monkeypatch:
    :return:
    """
    test_event_batch = EventBatch(
        user_id=20, user_email="fancyfrank@frankfurters.com", events=[]
    )

    with pytest.raises(ValueError):
        format_and_send_notifications(event_batch=test_event_batch)

    mock_send_via_mailgun.assert_not_called()
