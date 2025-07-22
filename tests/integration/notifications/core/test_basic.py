from db.dtos.event_batch import EventBatch
from endpoints.schema_config.instantiations.notifications_.core import (
    NotificationsPostEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.notifications_.preview import (
    NotificationsPreviewEndpointSchemaConfig,
)
from tests.helpers.constants import NOTIFICATIONS_BASE_ENDPOINT
from tests.helpers.helper_classes.test_data_creator.db_client_.core import (
    TestDataCreatorDBClient,
)
from tests.helpers.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)
from tests.helpers.run_and_validate_request import run_and_validate_request
from tests.integration.notifications.core._helpers.asserts import (
    assert_all_notifications_sent,
    assert_notification_log_created,
)
from tests.integration.notifications.core._helpers.call_checker.core import (
    EventBatchChecker,
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

    # Call preview and confirm expected response
    json_content = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="get",
        endpoint="/notifications/preview",
        headers=tus.jwt_authorization_header,
        expected_schema=NotificationsPreviewEndpointSchemaConfig.primary_output_schema,
    )
    assert json_content["counts"] == {
        "distinct_data_request_events": 3,
        "distinct_data_source_events": 1,
        "distinct_events": 4,
        "total_events": 4,
        "total_users": 2,
    }

    preview_event_batches = [
        EventBatch(**json_event_batch) for json_event_batch in json_content["batches"]
    ]

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
    calls = mock_format_and_send_notifications.call_args_list
    sent_event_batches = [call_.kwargs["event_batch"] for call_ in calls]
    assert len(sent_event_batches) == 2

    assert sent_event_batches == preview_event_batches

    checker = EventBatchChecker(sent_event_batches)
    checker.check_user(every_event_type_user_info)
    checker.check_user(single_event_type_user_info)

    assert_all_notifications_sent(tdc_db)

    assert_notification_log_created(tdc_db)
