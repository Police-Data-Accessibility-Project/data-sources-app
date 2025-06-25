from unittest.mock import call, ANY

from db.enums import EventType, EntityType
from db.models.implementations.core.log.notification import NotificationLog
from db.models.implementations.core.notification.queue.data_request import (
    DataRequestUserNotificationQueue,
)
from db.models.implementations.core.notification.queue.data_source import (
    DataSourceUserNotificationQueue,
)
from endpoints.schema_config.instantiations.notifications import (
    NotificationsPostEndpointSchemaConfig,
)
from middleware.custom_dataclasses import EventBatch, EventInfo
from tests.helper_scripts.constants import NOTIFICATIONS_BASE_ENDPOINT
from tests.helper_scripts.helper_classes.AnyOrder import AnyOrder
from tests.helper_scripts.helper_classes.test_data_creator.db_client_.core import (
    TestDataCreatorDBClient,
)
from tests.helper_scripts.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request


def test_notifications_followed_searches(
    test_data_creator_flask: TestDataCreatorFlask, mock_format_and_send_notifications
):
    tdc = test_data_creator_flask

    tdc_db = TestDataCreatorDBClient()
    tdc_db.clear_test_data()
    user_info = tdc_db.user()
    user_id = user_info.id
    request_ready_to_start_id = tdc_db.create_valid_notification_event(
        event_type=EventType.REQUEST_READY_TO_START, user_id=user_id
    )
    request_complete_id = tdc_db.create_valid_notification_event(
        event_type=EventType.REQUEST_COMPLETE, user_id=user_id
    )
    source_approved_id = tdc_db.create_valid_notification_event(
        event_type=EventType.DATA_SOURCE_APPROVED, user_id=user_id
    )

    # Add an additional user who will provide an additional batch
    additional_user_info = tdc_db.user()
    additional_user_id = additional_user_info.id
    additional_request_ready_to_start_id = tdc_db.create_valid_notification_event(
        event_type=EventType.REQUEST_READY_TO_START, user_id=additional_user_id
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
            "count": 2,
        },
        expected_schema=NotificationsPostEndpointSchemaConfig.primary_output_schema,
    )
    mock_format_and_send_notifications.assert_has_calls(
        any_order=True,
        calls=[
            call(
                event_batch=EventBatch(
                    user_id=user_id,
                    user_email=user_info.email,
                    events=AnyOrder(
                        [
                            EventInfo(
                                event_id=ANY,
                                event_type=EventType.REQUEST_READY_TO_START,
                                entity_id=request_ready_to_start_id,
                                entity_type=EntityType.DATA_REQUEST,
                                entity_name=ANY,
                            ),
                            EventInfo(
                                event_id=ANY,
                                event_type=EventType.REQUEST_COMPLETE,
                                entity_id=request_complete_id,
                                entity_type=EntityType.DATA_REQUEST,
                                entity_name=ANY,
                            ),
                            EventInfo(
                                event_id=ANY,
                                event_type=EventType.DATA_SOURCE_APPROVED,
                                entity_id=source_approved_id,
                                entity_type=EntityType.DATA_SOURCE,
                                entity_name=ANY,
                            ),
                        ]
                    ),
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
                            entity_name=ANY,
                        )
                    ],
                )
            ),
        ],
    )

    # Test that it calls the `format_and_send_notification` function with the requisite results 3 times

    # In the database, check that each notification has a non-null `sent_at`
    data_requests_queue = tdc_db.db_client.get_all(DataRequestUserNotificationQueue)
    assert len(data_requests_queue) == 3
    for data_request in data_requests_queue:
        assert data_request["sent_at"] is not None

    data_sources_queue = tdc_db.db_client.get_all(DataSourceUserNotificationQueue)
    assert len(data_sources_queue) == 1
    for data_source in data_sources_queue:
        assert data_source["sent_at"] is not None

    # Check that notification log was created
    notification_log = tdc_db.db_client.get_all(NotificationLog)
    assert len(notification_log) == 1
    assert notification_log[0]["created_at"] is not None
    assert notification_log[0]["user_count"] == 2
