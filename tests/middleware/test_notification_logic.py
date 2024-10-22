from unittest.mock import MagicMock

from database_client.enums import NotificationEntityType
from tests.helper_scripts.helper_schemas import TestGetPendingNotificationsOutputSchema


def test_send_user_notifications():

    # Patch db client's `get_pending_notifications` method to return
    # a list of test notifications

    test_data = [
        {
            "user_id": 1,
            "email": "test1@test.com",
            "event_name": "event_1",
            "entity_id": 1,
            "entity_type": NotificationEntityType.DATA_REQUEST.value,
            "entity_name": "test_entity_name1",
        },
        {
            "user_id": 1,
            "email": "test1@test.com",
            "event_name": "event_2",
            "entity_id": 2,
            "entity_type": NotificationEntityType.DATA_SOURCE.value,
            "entity_name": "test_entity_name3",
        },
        {
            "user_id": 2,
            "email": "test2@test.com",
            "event_name": "event_2",
            "entity_id": 2,
            "entity_type": NotificationEntityType.DATA_SOURCE.value,
            "entity_name": "test_entity_name2",
        }
    ]

    # Validate correctness of test data
    schema = TestGetPendingNotificationsOutputSchema(many=True)
    schema.load(test_data)

    mock_db_client = MagicMock()
    mock_db_client.get_pending_notifications.return_value = test_data

    send_user_notifications(mock_db_client)

    """
    TODO: Figure out how to handle atomic user notifications 
    -- There's a possibility that the notification sending might break partway through
    sending the emails.
    And in that case, we don't want to send them again. 
    
    We likely also want a log of all notifications sent out,
    so we could have a table which exists as both 
    a record of which notifications have been sent and
    which notifications have yet to be sent
    (with a timestamp column called `sent_at` which indicates when the notification was sent).
    """







