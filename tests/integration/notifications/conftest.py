from unittest.mock import MagicMock

import pytest

from db.enums import EntityType, EventType
from middleware.enums import RecordTypes
from tests.integration.notifications.core._helpers.models.entity_setup import (
    EntitySetupInfo,
)
from tests.integration.notifications.core._helpers.models.event_set import EventSetInfo

PATCH_ROOT = "middleware.primary_resource_logic.notifications"


@pytest.fixture
def mock_format_and_send_notifications(monkeypatch):
    mock_format_and_send_notifications = MagicMock()
    monkeypatch.setattr(
        f"{PATCH_ROOT}.format_and_send_notifications",
        mock_format_and_send_notifications,
    )
    return mock_format_and_send_notifications


@pytest.fixture
def setup_notifications(
    test_data_creator_db_client,
    allegheny_id,
    pittsburgh_id,
    pennsylvania_id,
    california_id,
):
    entity_setup_infos = [
        # DR PITTSBURGH ARREST_RECORD APPROVED_AND_COMPLETED
        EntitySetupInfo(
            location_id=pittsburgh_id,
            record_type=RecordTypes.ARREST_RECORDS,
            event_set_info=EventSetInfo(
                entity_type=EntityType.DATA_REQUEST,
                event_types=[
                    EventType.REQUEST_READY_TO_START,
                    EventType.REQUEST_COMPLETE,
                ],
            ),
        ),
        # DR PITTSBURGH COURT_CASES COMPLETED
        EntitySetupInfo(
            location_id=pittsburgh_id,
            record_type=RecordTypes.COURT_CASES,
            event_set_info=EventSetInfo(
                entity_type=EntityType.DATA_REQUEST,
                event_types=[EventType.REQUEST_COMPLETE],
            ),
        ),
        # DR COMPLETED ARREST_RECORD PENNSYLVANIA
        EntitySetupInfo(
            location_id=pennsylvania_id,
            record_type=RecordTypes.ARREST_RECORDS,
            event_set_info=EventSetInfo(
                entity_type=EntityType.DATA_REQUEST,
                event_types=[EventType.REQUEST_COMPLETE],
            ),
        ),
        # DS APPROVED ARREST_RECORD PENNSYLVANIA
        EntitySetupInfo(
            location_id=pennsylvania_id,
            record_type=RecordTypes.ARREST_RECORDS,
            event_set_info=EventSetInfo(
                entity_type=EntityType.DATA_SOURCE,
                event_types=[EventType.DATA_SOURCE_APPROVED],
            ),
        ),
        # DS APPROVED COURT_RECORD ALLEGHENY
        EntitySetupInfo(
            location_id=allegheny_id,
            record_type=RecordTypes.COURT_CASES,
            event_set_info=EventSetInfo(
                entity_type=EntityType.DATA_SOURCE,
                event_types=[EventType.DATA_SOURCE_APPROVED],
            ),
        ),
        # DS APPROVED COURT_RECORD CALIFORNIA
        EntitySetupInfo(
            location_id=california_id,
            record_type=RecordTypes.COURT_CASES,
            event_set_info=EventSetInfo(
                entity_type=EntityType.DATA_SOURCE,
                event_types=[EventType.DATA_SOURCE_APPROVED],
            ),
        ),
        # DS APPROVED ARREST_RECORD CALIFORNIA
        EntitySetupInfo(
            location_id=california_id,
            record_type=RecordTypes.ARREST_RECORDS,
            event_set_info=EventSetInfo(
                entity_type=EntityType.DATA_SOURCE,
                event_types=[EventType.DATA_SOURCE_APPROVED],
            ),
        ),
    ]
