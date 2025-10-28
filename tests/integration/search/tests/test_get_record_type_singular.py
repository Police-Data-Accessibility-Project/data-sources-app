from middleware.enums import RecordTypesEnum, Relations
from tests.integration.search.search_test_setup import SearchTestSetup


def test_search_get_record_type_singular(search_test_setup: SearchTestSetup):
    """
    The `record_type` parameter should be able to be provided as a singular value
    """
    sts = search_test_setup
    tdc = sts.tdc
    tus = sts.tus

    tdcdb = tdc.tdcdb
    record_types = list(RecordTypesEnum)
    for i in range(2):
        tdcdb.link_data_source_to_agency(
            data_source_id=tdcdb.data_source(record_type=record_types[i]).id,
            agency_id=tdcdb.agency(location_id=sts.location_id).id,
        )

    results = tdc.request_validator.search(
        headers=tus.api_authorization_header,
        location_id=sts.location_id,
        record_types=[RecordTypesEnum.ARREST_RECORDS],
    )
    assert results["count"] == 1
    assert (
        results["data"]["federal"]["results"][0]["record_type"]
        == RecordTypesEnum.ARREST_RECORDS.value
    )

    links = tdc.db_client._select_from_relation(
        relation_name=Relations.LINK_RECENT_SEARCH_RECORD_TYPES.value,
        columns=["record_type_id"],
    )
    assert len(links) == 1
    assert {link["record_type_id"] for link in links} == {2}
