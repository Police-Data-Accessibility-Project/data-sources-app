from middleware.enums import RecordTypesEnum, Relations
from tests.integration.search.search_test_setup import SearchTestSetup


def test_search_get_record_type_multiple(search_test_setup: SearchTestSetup):
    """
    The `record_type` parameter should be able to be provided as a list of values
    """
    sts = search_test_setup
    tdc = sts.tdc
    tus = sts.tus

    tdcdb = tdc.tdcdb
    record_types = list(RecordTypesEnum)
    for i in range(3):
        tdcdb.link_data_source_to_agency(
            data_source_id=tdcdb.data_source(record_type=record_types[i]).id,
            agency_id=tdcdb.agency(location_id=sts.location_id).id,
        )

    results = tdc.request_validator.search(
        headers=tus.api_authorization_header,
        location_id=sts.location_id,
        record_types=[RecordTypesEnum.ARREST_RECORDS, RecordTypesEnum.ACCIDENT_REPORTS],
    )
    assert results["count"] == 2

    links = tdc.db_client._select_from_relation(
        relation_name=Relations.LINK_RECENT_SEARCH_RECORD_TYPES.value,
        columns=["record_type_id"],
    )
    assert len(links) == 2
    assert {link["record_type_id"] for link in links} == {1, 2}
