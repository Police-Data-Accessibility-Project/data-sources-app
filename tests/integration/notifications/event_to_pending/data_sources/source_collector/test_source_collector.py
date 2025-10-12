"""
When a data source is added via the source collector,
the relevant event is added to the notification queue
"""

from endpoints.instantiations.source_collector.data_sources.post.dtos.request import (
    SourceCollectorPostRequestInnerDTO,
)
from middleware.enums import RecordTypes
from tests.integration.notifications.event_to_pending.data_sources.source_collector.manager import (
    EventToPendingDataSourcesSourceCollectorTestManager,
)


def test_data_source_added_from_source_collector(
    manager: EventToPendingDataSourcesSourceCollectorTestManager,
):
    agency_id = manager.tdc.agency().id
    dtos = [
        SourceCollectorPostRequestInnerDTO(
            name="Test Data Source 1",
            source_url="https://example.com/test1",
            record_type=RecordTypes.COURT_CASES,
            agency_ids=[agency_id],
        ),
        SourceCollectorPostRequestInnerDTO(
            name="Test Data Source 2",
            source_url="https://example.com/test2",
            record_type=RecordTypes.ACCIDENT_REPORTS,
            agency_ids=[agency_id],
        ),
    ]
    manager.db_client.add_data_sources_from_source_collector(dtos)
    manager.all_data_sources_in_queue(2)
