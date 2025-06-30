from sqlalchemy import select

from db.models.implementations.core.notification.pending.data_source import (
    DataSourcePendingEventNotification,
)


class EventToPendingDataSourcesTestManager:
    def __init__(self, tdc):
        self.tdc = tdc
        self.db_client = tdc.db_client

    def is_in_pending(self, data_source_id) -> bool:
        query = select(DataSourcePendingEventNotification.id).where(
            DataSourcePendingEventNotification.data_source_id == data_source_id
        )
        id_ = self.db_client.scalar(query)
        return id_ is not None
