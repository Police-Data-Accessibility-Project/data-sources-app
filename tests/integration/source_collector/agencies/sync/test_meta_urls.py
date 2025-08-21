from sqlalchemy import cast

from db.client.core import DatabaseClient
from db.enums import ApprovalStatus
from db.models.implementations.core.agency.core import Agency
from db.models.implementations.core.agency.meta_urls.sqlalchemy import AgencyMetaURL
from db.models.types import JurisdictionTypeEnum
from endpoints.instantiations.source_collector.agencies.sync.dtos.request import SourceCollectorSyncAgenciesRequestDTO
from middleware.enums import JurisdictionType, AgencyType
from tests.helpers.helper_classes.RequestValidator import RequestValidator
from tests.helpers.helper_classes.test_data_creator.flask import TestDataCreatorFlask


def test_source_collector_sync_agencies_meta_urls(
    test_data_creator_flask: TestDataCreatorFlask
):
    """
    Test that the source collector sync agencies endpoint returns all meta urls
    """

    tdc: TestDataCreatorFlask = test_data_creator_flask
    dbc: DatabaseClient = tdc.db_client
    rv: RequestValidator = tdc.request_validator
    # Add location to the database
    location_id: int = tdc.locality()

    # Add 2 agencies to the database, with multiple meta urls
    agencies = []
    for i in range(2):
        agency = Agency(
            name=f"Test Agency {i}",
            approval_status=ApprovalStatus.APPROVED.value,
            jurisdiction_type=cast(JurisdictionType.LOCAL.value, JurisdictionTypeEnum),
            agency_type=AgencyType.POLICE.value,
        )
        agencies.append(agency)

    agency_ids: list[int] = dbc.add_many(agencies, return_ids=True)

    # Add meta urls to the database
    meta_urls = []
    meta_url_objects: list[AgencyMetaURL] = []
    for agency_id in agency_ids:
        for i in range(2):
            url: str = f"https://example.com/agency/{agency_id}/meta_url/{i}"
            meta_urls.append(url)
            meta_url_obj = AgencyMetaURL(url=url, agency_id=agency_id)
            meta_url_objects.append(meta_url_obj)

    dbc.add_many(meta_url_objects, return_ids=False)

    results = rv.get_agencies_for_sync(
        headers=tdc.get_admin_tus().jwt_authorization_header,
        dto=SourceCollectorSyncAgenciesRequestDTO(page=1, updated_at=None),
    )['agencies']
    assert len(results) == 2
    result_meta_urls = []
    for result in results:
        assert len(result["meta_urls"]) == 2
        result_meta_urls.extend(result["meta_urls"])

    assert len(meta_urls) == len(result_meta_urls)
    assert set(meta_urls) == set(result_meta_urls)