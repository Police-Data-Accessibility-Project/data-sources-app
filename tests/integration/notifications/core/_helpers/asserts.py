from db.models.implementations.core.log.notification import NotificationLog
from db.models.implementations.core.notification.queue.data_request import (
    DataRequestUserNotificationQueue,
)
from db.models.implementations.core.notification.queue.data_source import (
    DataSourceUserNotificationQueue,
)


def assert_all_notifications_sent(tdc_db):
    """Check that each notification has a non-null `sent_at`"""
    data_requests_queue = tdc_db.db_client.get_all(DataRequestUserNotificationQueue)
    assert len(data_requests_queue) == 3
    for data_request in data_requests_queue:
        assert data_request["sent_at"] is not None
    data_sources_queue = tdc_db.db_client.get_all(DataSourceUserNotificationQueue)
    assert len(data_sources_queue) == 1
    for data_source in data_sources_queue:
        assert data_source["sent_at"] is not None


def assert_notification_log_created(tdc_db):
    """Check that notification log was created"""
    notification_log = tdc_db.db_client.get_all(NotificationLog)
    assert len(notification_log) == 1
    assert notification_log[0]["created_at"] is not None
    assert notification_log[0]["user_count"] == 2
