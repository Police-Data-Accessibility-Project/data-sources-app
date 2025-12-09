from middleware.enums import RecordTypesEnum
from utilities.enums import RecordCategoryEnum


def test_search_with_location_and_record_types_real_data_multiple_records(
    test_data_creator_db_client,
    live_database_client,
):
    pa_location_id = live_database_client.get_location_id(
        where_mappings={
            "state_name": "Pennsylvania",
            "county_name": None,
            "locality_name": None,
        }
    )
    tdc = test_data_creator_db_client

    def agency_and_data_source(
        location_id, record_type: RecordTypesEnum = RecordTypesEnum.LIST_OF_DATA_SOURCES
    ):
        ds_id = tdc.data_source(record_type=record_type).id
        a_id = tdc.agency(location_id=location_id).id
        tdc.link_data_source_to_agency(data_source_id=ds_id, agency_id=a_id)

    record_types = [record_type for record_type in RecordTypesEnum]
    for record_type in record_types:
        agency_and_data_source(pa_location_id, record_type=record_type)

    record_categories = []
    last_count = 0
    # Exclude the ALL pseudo-category
    applicable_record_categories = [
        e for e in RecordCategoryEnum if e != RecordCategoryEnum.ALL
    ]

    # Check that when more record types are added, the number of results increases
    for record_category in applicable_record_categories:
        record_categories.append(record_category)
        results = live_database_client.search_with_location_and_record_type(
            location_id=pa_location_id, record_categories=record_categories
        )
        assert len(results) > last_count, (
            f"{record_category} failed (total record_categories: {len(record_categories)})"
        )
        last_count = len(results)

    # Finally, check that all record_types is equivalent to no record types in terms of number of results
    results = live_database_client.search_with_location_and_record_type(
        location_id=pa_location_id
    )
    assert len(results) == last_count
