from middleware.custom_dataclasses import EventInfo
from tests.integration.notifications.core._helpers.models.event_set import EventSetInfo
from tests.integration.notifications.core._helpers.expected_event_info import (
    ExpectedEventInfo,
)


class EventInfoChecker:

    def __init__(self, event_infos: list[EventInfo]):
        self._entity_event_dict: dict[int, EventSetInfo] = {}

        for event_info in event_infos:
            assert isinstance(event_info, EventInfo)
            entity_id = event_info.entity_id
            if entity_id not in self._entity_event_dict:
                self._entity_event_dict[entity_id] = EventSetInfo(
                    entity_type=event_info.entity_type,
                    event_types=[event_info.event_type],
                )
            else:
                event_set_info = self._entity_event_dict[entity_id]
                event_set_info.event_types.append(event_info.event_type)

    def check_event_info(self, expected_event_info: ExpectedEventInfo):
        try:
            event_set_info = self._entity_event_dict[expected_event_info.entity_id]
        except KeyError:
            raise AssertionError(
                f"Could not find event info with entity id "
                f"{expected_event_info.entity_id} and event type "
                f"{expected_event_info.event_type}"
            )
        event_set_info.has_event_type(expected_event_info.event_type)
