from middleware.enums import RecordTypes
from tests.integration.search.search_test_setup import SearchTestSetup
from utilities.enums import RecordCategoryEnum


def test_search_get_record_categories_all(
    search_test_setup: SearchTestSetup,
):
    """
    All record categories can be provided in one of two ways:
    By explicitly passing an "ALL" value in the `record_categories` parameter
    Or by providing every non-ALL value in the `record_categories` parameter
    """
    sts = search_test_setup
    tdc = sts.tdc
    tus = sts.tus

    tdcdb = tdc.tdcdb
    record_types = list(RecordTypes)

    for i in range(2):
        tdcdb.link_data_source_to_agency(
            data_source_id=tdcdb.data_source(record_type=record_types[i]).id,
            agency_id=tdcdb.agency(location_id=sts.location_id).id,
        )

    def run_search(record_categories: list[RecordCategoryEnum]) -> dict:
        return tdc.request_validator.search(
            headers=tus.api_authorization_header,
            location_id=sts.location_id,
            record_categories=record_categories if len(record_categories) > 0 else None,
        )

    data_all_explicit = run_search(record_categories=[RecordCategoryEnum.ALL])
    assert data_all_explicit["count"] > 0

    # Check that the count is the same as if every record type is provided
    data_all_implicit = run_search(
        record_categories=[
            rc for rc in RecordCategoryEnum if rc != RecordCategoryEnum.ALL
        ]
    )
    assert data_all_implicit["count"] > 0
    assert data_all_implicit["count"] == data_all_explicit["count"]

    # Check that the count is the same if no record type is provided
    data_empty = run_search(record_categories=[])
    assert data_empty["count"] > 0
    assert data_empty["count"] == data_all_explicit["count"]
