from endpoints.instantiations.source_collector.data_sources.sync.dtos.request import (
    SourceCollectorSyncDataSourcesRequestDTO,
)
from tests.integration.source_collector.data_sources.sync.asserts import assert_data_sources_each_have_one_agency, \
    assert_expected_data_sources_count
from tests.integration.source_collector.data_sources.sync.request import (
    request_get_data_sources_for_sync,
)
from tests.integration.source_collector.data_sources.sync.setup import _generate_ds_agency_links, \
    _generate_test_data_sources, link_pending_agency_to_data_sources


def test_source_collector_sync_data_sources(
    test_data_creator_flask, test_agencies, sample_record_type_id, user_admin, tomorrow
):
    tdc = test_data_creator_flask
    dbc = test_data_creator_flask.db_client

    data_sources = _generate_test_data_sources(sample_record_type_id)
    data_source_ids = dbc.add_many(data_sources, return_ids=True)

    links = _generate_ds_agency_links(data_source_ids, test_agency_id=test_agencies[0])
    dbc.add_many(links, return_ids=False)
    # Generate a pending agency id and link to data sources as well
    link_pending_agency_to_data_sources(data_source_ids, dbc, tdc)

    rv = tdc.request_validator
    results = request_get_data_sources_for_sync(
        rv,
        headers=user_admin.jwt_authorization_header,
        dto=SourceCollectorSyncDataSourcesRequestDTO(),
    )
    assert_expected_data_sources_count(results=results, count=1000)
    assert_data_sources_each_have_one_agency(results)

    # Run again with a different page and get only one result
    results = request_get_data_sources_for_sync(
        rv,
        headers=user_admin.jwt_authorization_header,
        dto=SourceCollectorSyncDataSourcesRequestDTO(page=2),
    )
    assert_expected_data_sources_count(results=results, count=1)

    # Run again with an updated_at in the future and get no results
    results = request_get_data_sources_for_sync(
        rv,
        headers=user_admin.jwt_authorization_header,
        dto=SourceCollectorSyncDataSourcesRequestDTO(updated_at=tomorrow),
    )
    assert_expected_data_sources_count(results=results, count=0)


