import pytest

from db.client.core import DatabaseClient
from db.models.implementations.links.agency__location import LinkAgencyLocation
from db.models.implementations.core.agency.core import Agency
from middleware.enums import JurisdictionType, AgencyType


@pytest.fixture
def agency_id_1(pittsburgh_id: int, live_database_client: DatabaseClient) -> int:
    agency = Agency(
        name="Test Agency 1",
        jurisdiction_type=JurisdictionType.LOCAL.value,
        agency_type=AgencyType.POLICE.value,
        no_web_presence=False,
        defunct_year=None,
    )
    agency_id: int = live_database_client.add(agency, return_id=True)

    link = LinkAgencyLocation(
        agency_id=agency_id,
        location_id=pittsburgh_id,
    )
    live_database_client.add(link)

    return agency_id


@pytest.fixture
def agency_id_2(pennsylvania_id: int, live_database_client: DatabaseClient) -> int:
    agency = Agency(
        name="Test Agency 2",
        jurisdiction_type=JurisdictionType.STATE.value,
        agency_type=AgencyType.COURT.value,
        no_web_presence=True,
        defunct_year=None,
    )
    agency_id: int = live_database_client.add(agency, return_id=True)

    link = LinkAgencyLocation(
        agency_id=agency_id,
        location_id=pennsylvania_id,
    )
    live_database_client.add(link)

    return agency_id
