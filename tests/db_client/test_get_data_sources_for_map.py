from db.client.core import DatabaseClient
from db.enums import ApprovalStatus
from tests.helpers.helper_classes.test_data_creator.db_client_.core import TestDataCreatorDBClient
from tests.integration.test_check_database_health import wipe_database


def test_get_data_sources_for_map(
    live_database_client: DatabaseClient,
    test_data_creator_db_client: TestDataCreatorDBClient,
):
    wipe_database(live_database_client)
    tdc = test_data_creator_db_client
    location_id = tdc.locality()
    ds_id = tdc.data_source(approval_status=ApprovalStatus.APPROVED).id
    a_id = tdc.agency(
        location_id=location_id,
    ).id
    tdc.link_data_source_to_agency(
        data_source_id=ds_id,
        agency_id=a_id,
    )
    results = live_database_client.get_data_sources_for_map()
    assert len(results) > 0
    assert isinstance(results[0], live_database_client.MapInfo)
    assert results[0].location_id == location_id
