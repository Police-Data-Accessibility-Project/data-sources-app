from typing import Any, final

from sqlalchemy import select, Select, Executable

from db.models.implementations import (
    LinkLocationDataRequest,
    LinkUserFollowedLocation,
    LinkAgencyDataSource,
    LinkAgencyLocation,
)
from db.models.implementations.core.agency.core import Agency
from db.models.implementations.core.data_request.core import DataRequest
from db.models.implementations.core.data_source.core import DataSource
from db.models.implementations.core.location.core import Location
from db.models.implementations.core.notification.pending.data_request import (
    DataRequestPendingEventNotification,
)
from db.models.implementations.core.notification.pending.data_source import (
    DataSourcePendingEventNotification,
)
from db.models.implementations.core.notification.queue.data_request import (
    DataRequestUserNotificationQueue,
)
from db.models.implementations.core.notification.queue.data_source import (
    DataSourceUserNotificationQueue,
)
from db.models.implementations.core.user.core import User
from db.queries.builder.core import QueryBuilderBase
from db.queries.ctes.dependent_location import DependentLocationCTE


@final
class OptionallyUpdateUserNotificationQueueQueryBuilder(QueryBuilderBase):

    def __init__(self):
        super().__init__()
        self.dependent_locations = DependentLocationCTE()

    def add_queue_entries(
        self,
        queue_model: type[
            DataRequestUserNotificationQueue | DataSourceUserNotificationQueue
        ],
        query: Executable,
    ) -> None:
        raw_results = self.session.execute(query).mappings().all()
        for result in raw_results:
            queue = queue_model(
                user_id=result["user_id"],
                event_id=result["event_id"],
            )
            self.session.add(queue)
        self.session.flush()

    def run(self) -> None:
        """Clear and repopulates the user notification queue with new notifications."""
        # Get all data requests associated with the user's location that have a corresponding event
        # (and that event is not already in user_notification_queue for that user)
        data_request_query = self._build_data_request_query()

        raw_results = self.session.execute(data_request_query).mappings().all()
        for result in raw_results:
            queue = DataRequestUserNotificationQueue(
                user_id=result["user_id"],
                event_id=result["event_id"],
            )
            self.session.add(queue)
        self.session.flush()

        data_source_query = self._build_data_source_query()

        raw_results = self.session.execute(data_source_query).mappings().all()
        for result in raw_results:
            queue = DataSourceUserNotificationQueue(
                user_id=result["user_id"],
                event_id=result["event_id"],
            )
            self.session.add(queue)

    def _build_data_source_query(self):
        data_source_query = (
            select(
                DataSourcePendingEventNotification.id.label("event_id"),
                User.id.label("user_id"),
            )
            .select_from(User)
            # User follows location
            .join(
                LinkUserFollowedLocation,
                LinkUserFollowedLocation.user_id == User.id,
            )
            # Location has dependent locations
            .join(
                self.dependent_locations.query,
                self.dependent_locations.location_id
                == LinkUserFollowedLocation.location_id,
            )
            # Locations have agencies associated with them
            .outerjoin(
                LinkAgencyLocation,
                LinkAgencyLocation.location_id
                == self.dependent_locations.dependent_location_id,
            )
            # Agencies have data sources
            .join(
                LinkAgencyDataSource,
                LinkAgencyDataSource.agency_id == LinkAgencyLocation.agency_id,
            )
            # Data Sources have pending events
            .join(
                DataSourcePendingEventNotification,
                DataSourcePendingEventNotification.data_source_id
                == LinkAgencyDataSource.data_source_id,
            )
            .where(
                # Event ID should not be in user_notification_queue for that user
                DataSourcePendingEventNotification.id.notin_(
                    select(DataSourceUserNotificationQueue.event_id).where(
                        DataSourceUserNotificationQueue.user_id == User.id
                    )
                )
            )
        )
        return data_source_query

    def _build_data_request_query(self):
        data_request_query = (
            select(
                DataRequestPendingEventNotification.id.label("event_id"),
                User.id.label("user_id"),
            )
            .select_from(User)
            # User follows location
            .join(
                LinkUserFollowedLocation,
                LinkUserFollowedLocation.user_id == User.id,
            )
            # Location has dependent locations
            .join(
                self.dependent_locations.query,
                self.dependent_locations.location_id
                == LinkUserFollowedLocation.location_id,
            )
            # Locations have data requests associated with them
            .outerjoin(
                LinkLocationDataRequest,
                LinkLocationDataRequest.location_id
                == self.dependent_locations.dependent_location_id,
            )
            # Data requests have pending events
            .join(
                DataRequestPendingEventNotification,
                DataRequestPendingEventNotification.data_request_id
                == LinkLocationDataRequest.data_request_id,
            )
            .where(
                # Event ID should not be in user_notification_queue for that user
                DataRequestPendingEventNotification.id.notin_(
                    select(DataRequestUserNotificationQueue.event_id).where(
                        DataRequestUserNotificationQueue.user_id == User.id
                    )
                )
            )
        )
        return data_request_query
