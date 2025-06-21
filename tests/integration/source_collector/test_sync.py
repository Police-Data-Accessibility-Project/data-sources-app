import datetime

from sqlalchemy import cast, update, func, text, select

from db.enums import ApprovalStatus
from db.models.implementations import LinkAgencyLocation
from db.models.implementations.core.agency.core import Agency
from db.models.types import JurisdictionTypeEnum
from endpoints.instantiations.source_collector.sync.dtos.request import (
    SourceCollectorSyncAgenciesRequestDTO,
)
from middleware.enums import JurisdictionType, AgencyType
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)


def test_source_collector_sync_agencies(
    test_data_creator_flask: TestDataCreatorFlask,
):
    tdc = test_data_creator_flask
    dbc = tdc.db_client
    rv = tdc.request_validator
    # Add location to the database
    location_id = tdc.locality()

    today = datetime.datetime.now()
    # Add 1000 agencies to the database, receiving the agency ids
    agencies = []
    for i in range(1001):
        agency = Agency(
            name=f"Test Agency {i}",
            approval_status=ApprovalStatus.APPROVED.value,
            jurisdiction_type=cast(JurisdictionType.LOCAL.value, JurisdictionTypeEnum),
            agency_type=AgencyType.POLICE.value,
        )
        agencies.append(agency)
    agency_ids = dbc.add_many(agencies, return_ids=True)

    # Update the `updated_at` field of the ids to be equivalent to today - (1 day * id)
    stmt = f"""
    WITH ranked AS (
      SELECT
        id,
        ROW_NUMBER() OVER (ORDER BY id) AS rn
      FROM agencies
      WHERE agencies.id in ({", ".join(map(str, agency_ids))})
      LIMIT 1000
    )
    UPDATE agencies
    SET updated_at = CURRENT_DATE - INTERVAL '1 day' * ranked.rn
    FROM ranked
    WHERE agencies.id = ranked.id;
    """
    dbc.execute_raw_sql(stmt)

    # Link all to the location
    links = []
    for agency_id in agency_ids:
        link = LinkAgencyLocation(
            location_id=location_id,
            agency_id=agency_id,
        )
        links.append(link)
    dbc.add_many(links)

    results = rv.get_agencies_for_sync(
        headers=tdc.get_admin_tus().jwt_authorization_header,
        dto=SourceCollectorSyncAgenciesRequestDTO(page=1, updated_at=None),
    )
    # Check agencies retrieved in reverse order
    assert len(results["agencies"]) == 1000
    first_agency = results["agencies"][-1]
    assert first_agency["agency_id"] == agency_ids[0]
    last_agency = results["agencies"][0]
    assert last_agency["agency_id"] == agency_ids[-2]

    for i in range(1000):
        result_idx = 1000 - i - 1
        assert results["agencies"][result_idx]["display_name"] == f"Test Agency {i}"

    # Check pagination
    results_pagination = rv.get_agencies_for_sync(
        headers=tdc.get_admin_tus().jwt_authorization_header,
        dto=SourceCollectorSyncAgenciesRequestDTO(page=2, updated_at=None),
    )
    first_result_agency_ids = [result["agency_id"] for result in results["agencies"]]
    second_result_agency_ids = [
        result["agency_id"] for result in results_pagination["agencies"]
    ]
    assert len(second_result_agency_ids) == 1
    assert second_result_agency_ids[0] not in first_result_agency_ids

    # Apply datetime filtering and confirm some results filtered out
    results = rv.get_agencies_for_sync(
        headers=tdc.get_admin_tus().jwt_authorization_header,
        dto=SourceCollectorSyncAgenciesRequestDTO(
            page=1, updated_at=today.date() - datetime.timedelta(days=500)
        ),
    )
    assert len(results["agencies"]) in (501, 502)
