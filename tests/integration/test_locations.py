from dataclasses import dataclass

import pytest

from tests.helpers.common_test_data import get_test_name
from tests.helpers.helper_classes.MultiLocationSetup import MultiLocationSetup
from tests.helpers.helper_classes.test_data_creator.flask import (
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
        "location_id": location_id,
        "display_name": f"{locality_name}, Allegheny, Pennsylvania",
    }
    return LocationsTestSetup(tdc=tdc, location_info=loc_info)


def test_locations_get_by_id(locations_test_setup: LocationsTestSetup):
    lts = locations_test_setup
    tdc = lts.tdc

    # Get location, confirm information matches
    tdc.request_validator.get_location_by_id(
        location_id=lts.location_info["location_id"],
        headers=tdc.get_admin_tus().api_authorization_header,
        expected_json_content=lts.location_info,
    )


def test_locations_related_data_requests(locations_test_setup: LocationsTestSetup):
    lts = locations_test_setup
    tdc = lts.tdc
    location_id = lts.location_info["location_id"]

    # Add two data requests to location
    tdc.tdcdb.data_request(location_ids=[location_id])
    tdc.tdcdb.data_request(location_ids=[location_id])

    # Get data requests
    tus = tdc.standard_user()
    data = tdc.request_validator.get_location_related_data_requests(
        location_id=location_id,
        headers=tus.api_authorization_header,
    )

    # Confirm information matches
    assert len(data["data"]) == 2

    # Confirm also works with jwt
    data = tdc.request_validator.get_location_related_data_requests(
        location_id=location_id,
        headers=tus.jwt_authorization_header,
    )["data"]
    assert data[0]["locations"] == data[1]["locations"]
    assert data[0]["locations"][0]["location_id"] == location_id


def test_map_locations(test_data_creator_flask: TestDataCreatorFlask):
    tdc = test_data_creator_flask
    tdc.clear_test_data()
    mls = MultiLocationSetup(tdc.tdcdb)

    data = tdc.request_validator.get_locations_map(
        headers=tdc.get_admin_tus().api_authorization_header
    )

    states = data["states"]
    counties = data["counties"]
    localities = data["localities"]
    # Validate there are 3 states
    assert len(states) == 3
    # Validate there are 4 counties
    assert len(counties) == 4
    # Validate there is 1 locality (null lat/lng localities shouldn't appear)
    assert len(localities) == 1

    # Validate there are no data sources
    def no_data_sources(list_: list[dict]):
        for loc in list_:
            assert loc["source_count"] == 0

    no_data_sources(states)
    no_data_sources(counties)
    no_data_sources(localities)

    def add_data_sources(location_id: int, count: int):
        for i in range(count):
            # Create agency associated with location
            agency_id = tdc.agency(location_ids=[location_id]).id
            # Create data source
            data_source_id = tdc.data_source().id
            # Associate data source with agency
            tdc.link_data_source_to_agency(
                data_source_id=data_source_id, agency_id=agency_id
            )

    # Add data sources
    add_data_sources(location_id=mls.pittsburgh_id, count=2)
    add_data_sources(location_id=mls.allegheny_county_id, count=1)
    add_data_sources(location_id=mls.philadelphia_county_id, count=1)
    add_data_sources(location_id=mls.pennsylvania_id, count=1)
    add_data_sources(location_id=mls.orange_county_id, count=1)
    tdc.db_client.refresh_all_materialized_views()

    data = tdc.request_validator.get_locations_map(
        headers=tdc.get_admin_tus().api_authorization_header
    )
    states = data["states"]
    counties = data["counties"]
    localities = data["localities"]

    # Check all localities have county fips and state iso
    for locality in localities:
        assert locality["county_fips"] is not None
        assert locality["state_iso"] is not None

    # Check all counties have fips
    for county in counties:
        assert county["fips"] is not None

    ## VALIDATE DATA SOURCE COUNTS
    def check_location_source_count(name: str, data: list[dict], expected_value: int):
        for location in data:
            if location["name"] == name:
                assert location["source_count"] == expected_value
                return
        raise ValueError(f"Location {name} not found.")

    # Validate there are 2 data sources for the city of Pittsburgh
    check_location_source_count(name="Pittsburgh", data=localities, expected_value=2)

    # Validate there are 3 data sources for the county of Allegheny
    check_location_source_count(name="Allegheny", data=counties, expected_value=3)

    # Validate there is 1 data source for the county of Philadelphia
    check_location_source_count(name="Philadelphia", data=counties, expected_value=1)

    # Validate there are 5 data sources for the state of Pennsylvania
    check_location_source_count(name="Pennsylvania", data=states, expected_value=5)

    # Validate there is 1 data source for Orange County, California
    check_location_source_count(name="Orange", data=counties, expected_value=1)

    # Validate there is 1 data source for the state of California
    check_location_source_count(name="California", data=states, expected_value=1)


# TODO: Rebuild
# def test_get_many_locations(
#     live_database_client,
#     pennsylvania_id: int,
#     allegheny_id: int,
#     pittsburgh_id: int,
#     test_data_creator_flask: TestDataCreatorFlask
# ):
#     tdc = test_data_creator_flask
#     tdc.clear_test_data()
#
#     def get_many_locations(
#         page: int = 1,
#         has_coordinates: Optional[bool] = None,
#         type_: Optional[LocationType] = None,
#     ):
#         return tdc.request_validator.get_many_locations(
#             headers=tdc.get_admin_tus().jwt_authorization_header,
#             dto=LocationsGetRequestDTO(
#                 page=page,
#                 has_coordinates=has_coordinates,
#                 type=type_,
#             ),
#         )["results"]
#
#     # Run get many locations with no data and confirm no entries
#     data = get_many_locations()
#     assert len(data) == 3
#
#     # Filter on states and get expected location count
#     data = get_many_locations(type_=LocationType.STATE)
#     assert len(data) == 1
#
#     # Filter on counties and get expected location count
#     data = get_many_locations(type_=LocationType.COUNTY)
#     assert len(data) == 1
#
#     # Filter on localities and get expected location count
#     data = get_many_locations(type_=LocationType.LOCALITY)
#     assert len(data) == 1
#
#     # Set page to 2 and get no results
#     data = get_many_locations(page=2)
#     assert len(data) == 0
