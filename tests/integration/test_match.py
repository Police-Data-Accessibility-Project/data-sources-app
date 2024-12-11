from dataclasses import dataclass
from typing import Optional

import pytest
from conftest import test_data_creator_flask, monkeysession
from middleware.primary_resource_logic.match_logic import (
    try_matching_agency,
    AgencyMatchStatus,
)
from middleware.schema_and_dto_logic.primary_resource_dtos.match_dtos import (
    AgencyMatchInnerDTO,
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

    def additional_agency(self, locality_name: Optional[str] = None):
        return self.tdc.agency(
            location_info=get_sample_location_info(locality_name=locality_name)
        )


@pytest.fixture
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
    )


def test_agency_match_exact_match(
    match_agency_setup: TestMatchAgencySetup,
):
    mas = match_agency_setup

    dto = AgencyMatchInnerDTO(name=mas.agency_name, **mas.location_kwargs)
    amr = try_matching_agency(db_client=mas.tdc.db_client, dto=dto)
    assert amr.status == AgencyMatchStatus.EXACT


def test_agency_match_partial_match(match_agency_setup: TestMatchAgencySetup):
    mas = match_agency_setup

    # Add an additional agency with the same location information but different name
    # This should not be picked up.
    mas.additional_agency()
    modified_agency_name = mas.agency_name + "1"
    dto = AgencyMatchInnerDTO(name=modified_agency_name, **mas.location_kwargs)
    amr = try_matching_agency(db_client=mas.tdc.db_client, dto=dto)
    assert amr.status == AgencyMatchStatus.PARTIAL
    assert len(amr.agencies) == 1
    assert mas.agency_name in amr.agencies[0]["submitted_name"]


def test_agency_match_location_match(match_agency_setup: TestMatchAgencySetup):
    mas = match_agency_setup
    mas.additional_agency(locality_name=mas.location_kwargs["locality"])

    dto = AgencyMatchInnerDTO(name=get_test_name(), **mas.location_kwargs)
    amr = try_matching_agency(db_client=mas.tdc.db_client, dto=dto)
    assert amr.status == AgencyMatchStatus.LOCATION
    assert len(amr.agencies) == 2


def test_agency_match_no_match(match_agency_setup: TestMatchAgencySetup):
    mas = match_agency_setup

    dto = AgencyMatchInnerDTO(
        name=get_test_name(),
        state="New York",
        county="New York",
        locality=get_test_name(),
    )
    amr = try_matching_agency(db_client=mas.tdc.db_client, dto=dto)
    assert amr.status == AgencyMatchStatus.NO_MATCH


# region Test Full Integration


def test_agency_match_full_integration(test_data_creator_flask: TestDataCreatorFlask):

    location_1_info = get_sample_location_info()

    # Create a csv of possible agencies
    # One an exact match
    # One a partial match
    # One a location match
    # One a no match

    # Submit and confirm json received for each.


# endregion
