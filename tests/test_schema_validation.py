import itertools

import pytest
from marshmallow import ValidationError

from middleware.schema_and_dto.schemas.locations.info.base import (
    LocationInfoSchema,
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


