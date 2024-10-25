from http import HTTPStatus
from unittest.mock import MagicMock, call, ANY

import pytest

from database_client.enums import EventType, EntityType
from middleware.custom_dataclasses import EventInfo, EventBatch
from middleware.enums import Relations
from resources.endpoint_schema_config import SchemaConfigs
from tests.helper_scripts.common_test_data import TestDataCreatorFlask
from tests.helper_scripts.constants import NOTIFICATIONS_BASE_ENDPOINT
from tests.helper_scripts.helper_classes.AnyOrder import AnyOrder
from tests.helper_scripts.helper_classes.TestDataCreatorDBClient import TestDataCreatorDBClient
from conftest import test_data_creator_flask, monkeysession
from tests.helper_scripts.helper_classes.TestUserSetup import TestUserSetup
from tests.helper_scripts.run_and_validate_request import run_and_validate_request


PATCH_ROOT = "middleware.primary_resource_logic.notifications_logic"


@pytest.fixture
def mock_format_and_send_notifications(monkeypatch):
    mock_format_and_send_notifications = MagicMock()
    monkeypatch.setattr(
        f"{PATCH_ROOT}.format_and_send_notifications",
        mock_format_and_send_notifications
    )
    return mock_format_and_send_notifications


def test_notifications_followed_searches(
        test_data_creator_flask: TestDataCreatorFlask,
        mock_format_and_send_notifications
):
    tdc = test_data_creator_flask


    tdc_db = TestDataCreatorDBClient()
    tdc_db.clear_test_data()
    user_info = tdc_db.user()
    user_id = user_info.id
    request_ready_to_start_id = tdc_db.create_valid_notification_event(
        event_type=EventType.REQUEST_READY_TO_START,
        user_id=user_id
    )
    request_complete_id = tdc_db.create_valid_notification_event(
        event_type=EventType.REQUEST_COMPLETE,
        user_id=user_id
    )
    source_approved_id = tdc_db.create_valid_notification_event(
        event_type=EventType.DATA_SOURCE_APPROVED,
        user_id=user_id
    )

    # Add an additional user who will provide an additional batch
    additional_user_info = tdc_db.user()
    additional_user_id = additional_user_info.id
    additional_request_ready_to_start_id = tdc_db.create_valid_notification_event(
        event_type=EventType.REQUEST_READY_TO_START,
        user_id=additional_user_id
    )

    tus = tdc.notifications_user()

    # Call the notifications endpoint and confirm it returns a 200 status
    # With a message "Notifications sent successfully"
    run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="post",
        endpoint=NOTIFICATIONS_BASE_ENDPOINT,
        headers=tus.jwt_authorization_header,
        expected_json_content={
            "message": "Notifications sent successfully.",
            "count": 2
        },
        expected_schema=SchemaConfigs.NOTIFICATIONS_POST.value.output_schema
    )
    mock_format_and_send_notifications.assert_has_calls(
        any_order=True,
        calls=[
            call(
                event_batch=EventBatch(
                    user_id=user_id,
                    user_email=user_info.email,
                    events=AnyOrder([
                        EventInfo(
                            event_id=ANY,
                            event_type=EventType.REQUEST_READY_TO_START,
                            entity_id=request_ready_to_start_id,
                            entity_type=EntityType.DATA_REQUEST,
                            entity_name=ANY
                        ),
                        EventInfo(
                            event_id=ANY,
                            event_type=EventType.REQUEST_COMPLETE,
                            entity_id=request_complete_id,
                            entity_type=EntityType.DATA_REQUEST,
                            entity_name=ANY
                        ),
                        EventInfo(
                            event_id=ANY,
                            event_type=EventType.DATA_SOURCE_APPROVED,
                            entity_id=source_approved_id,
                            entity_type=EntityType.DATA_SOURCE,
                            entity_name=ANY
                        ),
                    ])
                )
            ),
            call(
                event_batch=EventBatch(
                    user_id=additional_user_id,
                    user_email=additional_user_info.email,
                    events=[
                        EventInfo(
                            event_id=ANY,
                            event_type=EventType.REQUEST_READY_TO_START,
                            entity_id=additional_request_ready_to_start_id,
                            entity_type=EntityType.DATA_REQUEST,
                            entity_name=ANY
                        )
                    ]
                )
            )
        ]
    )

    # Test that it calls the `format_and_send_notification` function with the requisite results 3 times

    # In the database, check that each notification has a non-null `sent_at`
    results = tdc_db.db_client._select_from_relation(
        relation_name=Relations.USER_NOTIFICATION_QUEUE.value,
        columns=[
            "id",
            "sent_at"
        ]
    )
    assert len(results) == 4
    for result in results:
        assert result["sent_at"] is not None

    # TODO: Create separate middleware test for `format_and_send_notification`

def test_notifications_permission_denied(
    test_data_creator_flask: TestDataCreatorFlask,
    mock_format_and_send_notifications
):
    """
    Test that for basic admins and standard users, they are not able to call the endpoint
    """
    tdc = test_data_creator_flask

    def run(tus: TestUserSetup):
        run_and_validate_request(
            flask_client=tdc.flask_client,
            http_method="post",
            endpoint=NOTIFICATIONS_BASE_ENDPOINT,
            headers=tus.jwt_authorization_header,
            expected_response_status=HTTPStatus.FORBIDDEN,
        )

    run(tdc.get_admin_tus())
    run(tdc.standard_user())