from unittest.mock import call, ANY

from db.enums import EventType, EntityType
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
from tests.integration.notifications.core._helpers.asserts import (
    assert_all_notifications_sent,
    assert_notification_log_created,
)
from tests.integration.notifications.core._helpers.call_checker.core import (
    FormatAndSendNotificationCallChecker,
)
from tests.integration.notifications.core._helpers.setup import (
    NotificationsTestSetupManager,
)


def test_notifications_followed_searches(
    test_data_creator_flask: TestDataCreatorFlask, mock_format_and_send_notifications
):
    tdc = test_data_creator_flask

    tdc_db = TestDataCreatorDBClient()
    setup_manager = NotificationsTestSetupManager(tdc=tdc_db)
    tdc_db.clear_test_data()
    every_event_type_user_info = setup_manager.create_every_event_type_user()
    single_event_type_user_info = setup_manager.create_single_event_type_user()

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
    checker = FormatAndSendNotificationCallChecker(mock_format_and_send_notifications)
    checker.check_user(every_event_type_user_info)
    checker.check_user(single_event_type_user_info)

    assert_all_notifications_sent(tdc_db)

    assert_notification_log_created(tdc_db)
