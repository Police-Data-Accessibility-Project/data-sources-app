from abc import ABC, abstractmethod

from db.client.core import DatabaseClient
from db.enums import EventType
from tests.integration.notifications.pending_to_queue._helpers.check_info import (
    CheckInfo,
)


class EventQueueCheckerBase(ABC):
    def __init__(self, db_client: DatabaseClient):
        self.db_client = db_client
        check_infos = self._get_notification_queue_check_infos()
        self._by_user = self._build_by_user_dictionary(check_infos)

    @abstractmethod
    def _get_notification_queue_check_infos(self) -> list[CheckInfo]:
        pass

    @staticmethod
    def _build_by_user_dictionary(check_infos):
        d = {}
        for check_info in check_infos:
            if check_info.user_id not in d:
                d[check_info.user_id] = []
            d[check_info.user_id].append(check_info)
        return d

    def user_has_event(
        self, user_id: int, entity_id: int, event_type: EventType
    ) -> bool:
        check_infos = self._by_user[user_id]
        for check_info in check_infos:
            if (
                check_info.entity_id == entity_id
                and check_info.event_type == event_type
            ):
                return True
        return False

    def _process_query(self, query) -> list[CheckInfo]:
        mappings = self.db_client.mappings(query)
        results = []
        for mapping in mappings:
            results.append(
                CheckInfo(
                    entity_id=mapping["entity_id"],
                    event_type=EventType(mapping["event_type"]),
                    user_id=mapping["user_id"],
                )
            )
        return results
