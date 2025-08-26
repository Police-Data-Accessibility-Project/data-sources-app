from db.client.core import DatabaseClient
from tests.helpers.helper_classes.test_data_creator.db_client_.core import (
    TestDataCreatorDBClient,
)


def test_multiple_municipalities(
    live_database_client: DatabaseClient,
    test_data_creator_db_client: TestDataCreatorDBClient,
    pennsylvania_id: int,
):
    tdc = test_data_creator_db_client
    locality_1_id: int = tdc.locality(state_iso="PA")
    locality_2_id: int = tdc.locality(state_iso="PA")

    agency_id: int = tdc.agency().id
    live_database_client.add_location_to_agency(
        agency_id=agency_id,
        location_id=locality_1_id,
    )
    live_database_client.add_location_to_agency(
        agency_id=agency_id,
        location_id=locality_2_id,
    )

    ds_id_1: int = tdc.data_source().id

    tdc.link_data_source_to_agency(
        data_source_id=ds_id_1,
        agency_id=agency_id,
    )

    results = live_database_client.search_with_location_and_record_type(
        location_id=pennsylvania_id,
    )

    # Test that despite the agency being linked to multiple municipalities, only one result is returned
    assert len(results) == 1
    result = results[0]

    # Test that the municipality is comma-delimited, to denote multiple municipalities
    assert "," in result["municipality"]
