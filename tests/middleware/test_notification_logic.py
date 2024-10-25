import os
from unittest import mock

import pytest

from database_client.enums import EventType, EntityType
from middleware.custom_dataclasses import EventBatch, EventInfo
from middleware.primary_resource_logic.notifications_logic import format_and_send_notifications
from tests.helper_scripts.common_mocks_and_patches import patch_and_return_mock

PATCH_ROOT = "middleware.primary_resource_logic.notifications_logic"

class SpaceAgnosticStringComparator:
    """
    Used to compare two strings without taking spaces into account
    """

    def __init__(self, s: str):
        self.s = s

    def __eq__(self, other: str):
        return self.s.replace(" ", "") != other.replace(" ", "")

    def __ne__(self, other: str):
        return self.s.replace(" ", "") != other.replace(" ", "")

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
        envvars = {
            "VITE_VUE_APP_BASE_URL": "https://test.com"
        }
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
    return patch_and_return_mock(
        f"{PATCH_ROOT}.send_via_mailgun", monkeypatch
    )

def test_format_and_send_notification_all_categories(
    mock_send_via_mailgun,
    mock_vite_vue_app_base_url
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
                entity_name="Test Data Request 1"
            ),
            EventInfo(
                event_id=2,
                event_type=EventType.REQUEST_COMPLETE,
                entity_id=45,
                entity_type=EntityType.DATA_REQUEST,
                entity_name="Test Data Request 2"
            ),
            EventInfo(
                event_id=3,
                event_type=EventType.DATA_SOURCE_APPROVED,
                entity_id=52,
                entity_type=EntityType.DATA_SOURCE,
                entity_name="Test Data Source 1"
            ),
            EventInfo(
                event_id=4,
                event_type=EventType.DATA_SOURCE_APPROVED,
                entity_id=79,
                entity_type=EntityType.DATA_SOURCE,
                entity_name="Test Data Source 2"
            )
        ]
    )

    format_and_send_notifications(
        event_batch=test_event_batch
    )

    html_text = """
<p>There have been updates to locations you've followed.
</br>
<h1>New Data Sources Approved</h1>
<p>The following data sources associated with your followed locations have been approved:</p>
<ul>
	<li><a href="https://test.com/data-source/52">Test Data Source 1</a></li>
	<li><a href="https://test.com/data-source/79">Test Data Source 2</a></li>
</ul>
</br>
<h1>Data Requests Completed</h1>
<p>The following data requests associated with your followed locations have been completed:</p>
<ul>
	<li><a href="https://test.com/data-request/45">Test Data Request 2</a></li>
</ul>
</br>
<h1>Data Requests Ready to Start</h1>
<p>The following data requests associated with your followed locations have been marked as 'Ready to Start':</p>
<ul>
	<li><a href="https://test.com/data-request/39">Test Data Request 1</a></li>
</ul>
</br>
<p>Click <a href="https://test.com/user/20">here</a> to view and update your user profile.
    """

    text = """
There have been updates to locations you've followed.

New Data Sources Approved
The following data sources associated with your followed locations have been approved:
- Test Data Source 1 at https://test.com/data-source/52
- Test Data Source 2 at https://test.com/data-source/79

Data Requests Completed
The following data requests associated with your followed locations have been completed:
- Test Data Request 2 at https://test.com/data-request/45

Data Requests Ready to Start
The following data requests associated with your followed locations have been marked as 'Ready to Start':
- Test Data Request 1 at https://test.com/data-request/39

Click the following link to view and update your user profile: https://test.com/user/20
    """

    mock_send_via_mailgun.assert_called_once_with(
        to_email=test_event_batch.user_email,
        subject="Updates to your followed searches this month",
        text="Test",
        html="Test"
    )



def test_format_and_send_notification_single_category(
    mock_send_via_mailgun,
    mock_vite_vue_app_base_url
):

    """
    Test that when a category is not included, the header doesn't appear
    :param monkeypatch:
    :return:
    """
    pytest.fail()




def test_format_and_send_notifications_error_no_events(
    mock_send_via_mailgun,
    mock_vite_vue_app_base_url
):
    """
    Test that an error is thrown when there are no events included in the batch
    :param monkeypatch:
    :return:
    """
    pytest.fail()
