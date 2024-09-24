import itertools

import pytest
from marshmallow import ValidationError

from middleware.enums import JurisdictionType
from middleware.primary_resource_logic.agencies import (
    LocationInfoSchema,
    AgenciesPostSchema,
)


def test_location_info_schema_validation_errors():
    """
    Test that all expected scenarios which are meant to produce validation errors properly produce validation errors
    :return:
    """
    location_types = ["State", "County", "Locality"]
    booleans = [True, False]
    VALID_LOCATION_INFO_PARAMS = [
        ("State", True, False, False),
        ("County", True, True, False),
        ("Locality", True, True, True),
    ]

    def generate_fake_data(
        location_type: str, state: bool, county: bool, locality: bool
    ):
        data = {"type": location_type}
        if state:
            data["state_iso"] = "CA"
        if county:
            data["county_fips"] = "06001"
        if locality:
            data["locality_name"] = "Los Angeles"
        return data

    def generate_fake_data_with_nones(
        location_type: str, state: bool, county: bool, locality: bool
    ):
        data = {"type": location_type}
        data["state_iso"] = "CA" if state else None
        data["county_fips"] = "06001" if county else None
        data["locality_name"] = "Los Angeles" if locality else None
        return data

    all_combinations = list(
        itertools.product(location_types, booleans, booleans, booleans)
    )
    for combination in all_combinations:
        data = generate_fake_data(*combination)
        data_with_nones = generate_fake_data_with_nones(*combination)
        if combination in VALID_LOCATION_INFO_PARAMS:
            try:
                LocationInfoSchema().load(data)
            except ValidationError as e:
                pytest.fail(f"Unexpected validation error for {data}: {e}")
            try:
                LocationInfoSchema().load(data_with_nones)
            except ValidationError as e:
                pytest.fail(f"Unexpected validation error for {data_with_nones}: {e}")
        else:
            with pytest.raises(ValidationError):
                LocationInfoSchema().load(data)
                pytest.fail(f"Expected validation error for {data}")
            with pytest.raises(ValidationError):
                LocationInfoSchema().load(data_with_nones)
                pytest.fail(f"Expected validation error for {data}")


def test_agencies_post_schema():
    schema = AgenciesPostSchema()
    def produce_data(jurisdiction_type: JurisdictionType, include_location_info: bool = True):
        data = {
            "agency_info": {
                "submitted_name": "test",
                "airtable_uid": "test",
                "jurisdiction_type": jurisdiction_type.value,
            }
        }
        if include_location_info:
            data["location_info"] = {
                "type": "Locality",
                "state_iso": "CA",
                "county_fips": "06001",
                "locality_name": "Los Angeles",
            }
        return data

    for jurisdiction_type in JurisdictionType:
        if jurisdiction_type == JurisdictionType.FEDERAL:
            # If location info is included, validation should not pass
            with pytest.raises(ValidationError):
                schema.load(produce_data(jurisdiction_type))
            # Conversely, if location info is not included, validation should pass
            schema.load(produce_data(jurisdiction_type, include_location_info=False))
        else:
            # If location info is included, validation should pass
            schema.load(produce_data(jurisdiction_type))
            # Conversely, if location info is not included, validation should fail
            with pytest.raises(ValidationError):
                schema.load(produce_data(jurisdiction_type, include_location_info=False))

def test_agencies_put_schema_location_info_only():
    schema = AgenciesPostSchema()
    with pytest.raises(ValidationError):
        schema.load({
            "agency_info": None,
            "location_info": {
                "location_type": "Locality",
                "state_iso": "CA",
                "county_fips": "06001",
                "locality_name": "Los Angeles",
            }
        })

def test_agencies_put_schema_location_info_and_no_jurisdiction_type():
    schema = AgenciesPostSchema()
    with pytest.raises(ValidationError):
        schema.load({
            "agency_info": {
                "submitted_name": "test",
            },
            "location_info": {
                "location_type": "Locality",
                "state_iso": "CA",
                "county_fips": "06001",
                "locality_name": "Los Angeles",
            }
        })