from unittest.mock import MagicMock

import pytest

from database_client.db_client_dataclasses import WhereMapping
from database_client.enums import LocationType
from middleware.primary_resource_logic.agencies import (
    get_location_id,
    InvalidLocationError,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.agencies import LocationInfoDTO


@pytest.fixture
def mock():
    mock = MagicMock()
    return mock


COUNTY_DTO = LocationInfoDTO(
    type=LocationType.COUNTY,
    state_iso="NY",
    county_fips="123",
)


def test_get_location_id_happy_path(mock):
    mock.db_client.get_location_id.return_value = [{"id": 1}]
    result = get_location_id(db_client=mock.db_client, location_info=COUNTY_DTO)
    assert result == 1
    mock.db_client.get_location_id.assert_called_once_with(
        where_mappings=WhereMapping.from_dict(
            {
                "type": LocationType.COUNTY,
                "state_iso": "NY",
                "county_fips": "123",
                "locality_name": None,
            }
        )
    )


def test_get_location_id_location_not_exists_not_locality(mock):
    mock.db_client.get_location_id.return_value = []
    with pytest.raises(InvalidLocationError):
        get_location_id(db_client=mock.db_client, location_info=COUNTY_DTO)
    mock.db_client.get_location_id.assert_called_once_with(
        where_mappings=WhereMapping.from_dict(
            {
                "type": LocationType.COUNTY,
                "state_iso": "NY",
                "county_fips": "123",
                "locality_name": None,
            }
        )
    )


def test_get_location_id_invalid_county(mock):
    mock.db_client.get_location_id.side_effect = [[], []]
    with pytest.raises(InvalidLocationError):
        get_location_id(db_client=mock.db_client, location_info=COUNTY_DTO)

