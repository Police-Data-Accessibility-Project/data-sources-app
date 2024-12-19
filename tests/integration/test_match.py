from dataclasses import dataclass
from typing import Optional

import pytest
from conftest import test_data_creator_flask, monkeysession
from middleware.primary_resource_logic.match_logic import (
    try_matching_agency,
    AgencyMatchStatus,
)
from middleware.schema_and_dto_logic.primary_resource_dtos.match_dtos import (
    AgencyMatchDTO,
)
from tests.helper_scripts.common_test_data import get_test_name
from tests.helper_scripts.complex_test_data_creation_functions import (
    get_sample_location_info,
)
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)


class TestMatchLocationInfo:
    def __init__(self, tdc: TestDataCreatorFlask):
        self.tdc = tdc
        self.locality_name = get_test_name()
        self.locality_id = self.tdc.locality(locality_name=self.locality_name)
        self.location_info = get_sample_location_info(locality_name=self.locality_name)
        self.location_kwargs = {
            "state": "Pennsylvania",
            "county": "Allegheny",
            "locality": self.locality_name,
        }


@dataclass
class TestMatchAgencySetup:
    tdc: TestDataCreatorFlask
    location_kwargs: dict
    agency_name: str
    jwt_authorization_header: dict

    def additional_agency(self, locality_name: Optional[str] = None):
        return self.tdc.agency(
            location_info=get_sample_location_info(locality_name=locality_name)
        )


@pytest.fixture()
def match_agency_setup(
    test_data_creator_flask: TestDataCreatorFlask,
) -> TestMatchAgencySetup:
    tdc = test_data_creator_flask
    tdc.clear_test_data()
    loc_info: TestMatchLocationInfo = TestMatchLocationInfo(tdc)
    agency = tdc.agency(location_info=loc_info.location_info)
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
        **mas.location_kwargs
    )

    assert data["status"] == AgencyMatchStatus.EXACT.value
    assert mas.agency_name in data["agencies"][0]["submitted_name"]


def test_agency_match_partial_match(match_agency_setup: TestMatchAgencySetup):
    mas = match_agency_setup

    # Add an additional agency with the same location information but different name
    # This should not be picked up.
    mas.additional_agency()
    modified_agency_name = mas.agency_name + "1"
    data = mas.tdc.request_validator.match_agency(
        headers=mas.jwt_authorization_header,
        name=modified_agency_name,
        **mas.location_kwargs
    )

    assert data["status"] == AgencyMatchStatus.PARTIAL.value
    assert len(data["agencies"]) == 1
    assert mas.agency_name in data["agencies"][0]["submitted_name"]


def test_agency_match_location_match(match_agency_setup: TestMatchAgencySetup):
    mas = match_agency_setup
    mas.additional_agency(locality_name=mas.location_kwargs["locality"])

    data = mas.tdc.request_validator.match_agency(
        headers=mas.jwt_authorization_header,
        name=get_test_name(),
        **mas.location_kwargs
    )
    assert data["status"] == AgencyMatchStatus.NO_MATCH.value


def test_agency_match_no_match(match_agency_setup: TestMatchAgencySetup):
    mas = match_agency_setup
    data = mas.tdc.request_validator.match_agency(
        headers=mas.jwt_authorization_header,
        name=get_test_name(),
        state="New York",
        county="New York",
        locality=get_test_name(),
    )


# region Test Full Integration
