from db.client.core import DatabaseClient
from db.enums import ApprovalStatus
from db.models.implementations import LinkAgencyDataSource
from db.models.implementations.core.data_source.core import DataSource
from tests.helpers.helper_classes.test_data_creator.flask import TestDataCreatorFlask


def _generate_ds_agency_links(data_source_ids: list[int], test_agency_id: int):
    links = []
    for data_source_id in data_source_ids:
        link = LinkAgencyDataSource(
            data_source_id=data_source_id,
            agency_id=test_agency_id,
        )
        links.append(link)
    return links


def _generate_test_data_sources(sample_record_type_id: int):
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


def link_pending_agency_to_data_sources(
    data_source_ids: list[int],
    dbc: DatabaseClient,
    tdc: TestDataCreatorFlask
):
    pending_agency = tdc.agency(approval_status=ApprovalStatus.PENDING)
    links = _generate_ds_agency_links(data_source_ids, test_agency_id=pending_agency.id)
    dbc.add_many(links, return_ids=False)
