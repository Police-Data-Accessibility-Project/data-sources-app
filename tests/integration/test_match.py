from dataclasses import dataclass
from typing import Optional

import pytest
from middleware.primary_resource_logic.match import (
    AgencyMatchStatus,
)
from tests.helper_scripts.common_test_data import get_test_name
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)


class TestMatchLocationInfo:
    def __init__(self, tdc: TestDataCreatorFlask):
        self.tdc = tdc
        self.locality_name = get_test_name()
        self.locality_id = self.tdc.locality(locality_name=self.locality_name)
        self.location_kwargs = {
            "state_name": "Pennsylvania",
            "county_name": "Allegheny",
            "locality_name": self.locality_name,
        }


@dataclass
class TestMatchAgencySetup:
    tdc: TestDataCreatorFlask
    location_kwargs: dict
    agency_name: str
    jwt_authorization_header: dict

    def additional_agency(
        self, location_id: Optional[int] = None, agency_name: str = ""
    ):
        return self.tdc.agency(
            location_ids=[location_id] if location_id is not None else None,
            agency_name=agency_name,
            add_test_name=False,
        )


@pytest.fixture()
def match_agency_setup(
    test_data_creator_flask: TestDataCreatorFlask,
) -> TestMatchAgencySetup:
    tdc = test_data_creator_flask
    tdc.clear_test_data()
    loc_info: TestMatchLocationInfo = TestMatchLocationInfo(tdc)
    agency = tdc.agency(location_ids=[loc_info.locality_id])
    return TestMatchAgencySetup(
        tdc=tdc,
        location_kwargs=loc_info.location_kwargs,
        agency_name=agency.submitted_name,
        jwt_authorization_header=tdc.get_admin_tus().jwt_authorization_header,
    )


def test_agency_match_exact_match(
    match_agency_setup: TestMatchAgencySetup,
):
    mas = match_agency_setup

    data = mas.tdc.request_validator.match_agency(
        headers=mas.jwt_authorization_header,
        name=mas.agency_name,
        state=mas.location_kwargs["state_name"],
        county=mas.location_kwargs["county_name"],
        locality=mas.location_kwargs["locality_name"],
    )

    assert data["status"] == AgencyMatchStatus.EXACT.value
    assert mas.agency_name in data["agencies"][0]["name"]


def test_agency_match_partial_match(match_agency_setup: TestMatchAgencySetup):
    mas = match_agency_setup

    # Add an additional agency with the same location information but different name
    # This should not be picked up.
    mas.additional_agency()
    # Create another agency with a slightly different name and the same location
    # This should be picked up
    location_id = mas.tdc.db_client.get_location_id(where_mappings=mas.location_kwargs)

    mas.additional_agency(
        agency_name=mas.agency_name + "2",
        location_id=location_id,
    )

    modified_agency_name = mas.agency_name + "1"
    data = mas.tdc.request_validator.match_agency(
        headers=mas.jwt_authorization_header,
        name=modified_agency_name,
        state=mas.location_kwargs["state_name"],
        county=mas.location_kwargs["county_name"],
        locality=mas.location_kwargs["locality_name"],
    )

    assert data["status"] == AgencyMatchStatus.PARTIAL.value
    assert len(data["agencies"]) == 2
    assert mas.agency_name in data["agencies"][0]["name"]


def test_agency_match_partial_match_no_location_data(
    match_agency_setup: TestMatchAgencySetup,
):
    mas = match_agency_setup
    for i in range(11):
        mas.additional_agency()

    data = mas.tdc.request_validator.match_agency(
        headers=mas.jwt_authorization_header, name="TEST"
    )

    assert data["status"] == AgencyMatchStatus.PARTIAL.value
    assert len(data["agencies"]) == 10


def test_agency_match_no_match(match_agency_setup: TestMatchAgencySetup):
    mas = match_agency_setup
    data = mas.tdc.request_validator.match_agency(
        headers=mas.jwt_authorization_header,
        name=get_test_name(),
        state="New York",
        county="New York",
        locality=get_test_name(),
    )
    assert data["status"] == AgencyMatchStatus.NO_MATCH.value


# region Test Full Integration
