from dataclasses import dataclass

import pytest

from conftest import test_data_creator_flask, monkeysession
from tests.helper_scripts.common_test_data import get_test_name
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)


@dataclass
class LocationsTestSetup:
    tdc: TestDataCreatorFlask
    location_info: dict


@pytest.fixture
def locations_test_setup(test_data_creator_flask: TestDataCreatorFlask):
    tdc = test_data_creator_flask
    # Create location
    locality_name = get_test_name()
    location_id = tdc.locality(locality_name=get_test_name())
    loc_info = {
        "state_name": "Pennsylvania",
        "state_iso": "PA",
        "type": "Locality",
        "county_name": "Allegheny",
        "county_fips": "42003",
        "locality_name": locality_name,
        "id": location_id,
    }
    return LocationsTestSetup(tdc=tdc, location_info=loc_info)


def test_locations_get_by_id(locations_test_setup: LocationsTestSetup):
    lts = locations_test_setup
    tdc = lts.tdc

    # Get location, confirm information matches
    data = tdc.request_validator.get_location_by_id(
        location_id=lts.location_info["id"],
        headers=tdc.get_admin_tus().jwt_authorization_header,
        expected_json_content=lts.location_info,
    )


def test_locations_related_data_requests(locations_test_setup: LocationsTestSetup):
    lts = locations_test_setup
    tdc = lts.tdc

    # Add two data requests to location
    dr_1 = tdc.data_request(location_ids=[lts.location_info["id"]]).id
    dr_2 = tdc.data_request(location_ids=[lts.location_info["id"]]).id

    # Get data requests
    tus = tdc.standard_user()
    data = tdc.request_validator.get_location_related_data_requests(
        location_id=lts.location_info["id"],
        headers=tus.api_authorization_header,
    )

    # Confirm information matches
    assert len(data["data"]) == 2

    # Confirm also works with jwt
    data = tdc.request_validator.get_location_related_data_requests(
        location_id=lts.location_info["id"],
        headers=tus.jwt_authorization_header,
    )
