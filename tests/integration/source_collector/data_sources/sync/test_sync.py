from db.enums import ApprovalStatus
from db.models.implementations import LinkAgencyDataSource
from db.models.implementations.core.data_source.core import DataSource
from endpoints.instantiations.source_collector.data_sources.sync.dtos.request import (
    SourceCollectorSyncDataSourcesRequestDTO,
)
from tests.integration.source_collector.data_sources.sync.request import (
    request_get_data_sources_for_sync,
)


def test_source_collector_sync_data_sources(
    test_data_creator_flask, test_agencies, sample_record_type_id, user_admin, tomorrow
):
    tdc = test_data_creator_flask
    dbc = test_data_creator_flask.db_client

    data_sources = _generate_test_data_sources(sample_record_type_id)
    data_source_ids = dbc.add_many(data_sources, return_ids=True)

    links = _generate_ds_agency_links(data_source_ids, test_agency_id=test_agencies[0])
    dbc.add_many(links, return_ids=False)
    # Generate a rejected agency id and link to data sources as well
    pending_agency = tdc.agency(approval_status=ApprovalStatus.PENDING)
    links = _generate_ds_agency_links(data_source_ids, test_agency_id=pending_agency.id)
    dbc.add_many(links, return_ids=False)

    rv = tdc.request_validator
    results = request_get_data_sources_for_sync(
        rv,
        headers=user_admin.jwt_authorization_header,
        dto=SourceCollectorSyncDataSourcesRequestDTO(),
    )
    # Check data sources retrieved in reverse order
    assert len(results["data_sources"]) == 1000
    # Check all data sources have only one agency associated with them
    for data_source in results["data_sources"]:
        assert len(data_source["agency_ids"]) == 1

    # Run again with a different page and get only one result
    results = request_get_data_sources_for_sync(
        rv,
        headers=user_admin.jwt_authorization_header,
        dto=SourceCollectorSyncDataSourcesRequestDTO(page=2),
    )
    assert len(results["data_sources"]) == 1

    # Run again with an updated_at in the future and get no results
    results = request_get_data_sources_for_sync(
        rv,
        headers=user_admin.jwt_authorization_header,
        dto=SourceCollectorSyncDataSourcesRequestDTO(updated_at=tomorrow),
    )
    assert len(results["data_sources"]) == 0


def _generate_ds_agency_links(data_source_ids, test_agency_id: int):
    links = []
    for data_source_id in data_source_ids:
        link = LinkAgencyDataSource(
            data_source_id=data_source_id,
            agency_id=test_agency_id,
        )
        links.append(link)
    return links


def _generate_test_data_sources(sample_record_type_id):
    data_sources = []
    for i in range(1001):
        if i % 2 == 0:
            description = f"Test Data Source {i}, created by test_source_collector_sync_data_sources()"
        else:
            description = None

        data_source = DataSource(
            name=f"Test Data Source {i}",
            source_url=f"https://test.com/{i}",
            approval_status=ApprovalStatus.APPROVED.value,
            description=description,
            record_type_id=sample_record_type_id,
        )
        data_sources.append(data_source)
    return data_sources
