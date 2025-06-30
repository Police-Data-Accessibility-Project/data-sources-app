from collections import defaultdict

from db.dtos.event_info import EventInfo
from db.enums import EventType
from tests.integration.notifications.core._helpers.expected_event_info import (
    ExpectedEventInfo,
)


class EventInfoChecker:
    def __init__(self, event_infos: list[EventInfo]):
        self._entity_event_dict: dict[int, EventInfo] = {
            getattr(event_info, "event_id"): event_info for event_info in event_infos
        }
        self._entity_id_to_event_types: dict[int, set[EventType]] = defaultdict(set)
        for event_info in event_infos:
            self._entity_id_to_event_types[event_info.entity_id].add(
                event_info.event_type
            )

    def has_entity_event_with_type(
        self, entity_id: int, expected_event_type: EventType
    ):
        """Check that the expected event type exists for the associated entity"""
        try:
            event_type_set = self._entity_id_to_event_types[entity_id]
            if expected_event_type in event_type_set:
                return
        except KeyError:
            pass
        raise AssertionError(
            f"Could not find event info with entity id {entity_id} and event type {expected_event_type}"
        )

    def check_event_info(self, expected_event_info: ExpectedEventInfo):
        """Check that a given event exists for the associated entity and has the expected event type"""
        self.has_entity_event_with_type(
            entity_id=expected_event_info.entity_id,
            expected_event_type=expected_event_info.event_type,
        )
