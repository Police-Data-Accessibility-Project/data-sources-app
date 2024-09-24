"""
These functions test various database-internal views and functions.
This is distinct from the functions in the `database_client` module
which test the database-external views and functions
"""

from collections import namedtuple

import psycopg
import pytest

from database_client.database_client import DatabaseClient
from database_client.db_client_dataclasses import WhereMapping
from middleware.enums import Relations
from tests.fixtures import live_database_client

ID_COLUMN = "state_iso"
FAKE_STATE_INFO = {"state_iso": "ZZ", "state_name": "Zaldoniza"}
FAKE_COUNTY_INFO = {"fips": "54321", "name": "Zipzapzibbidybop", "state_iso": "ZZ"}
FAKE_LOCALITY_INFO = {"name": "Zoolazoolio"}

FakeLocationsInfo = namedtuple(
    "FakeLocationsInfo", ["state_id", "county_id", "locality_id"]
)

@pytest.fixture
def setup_fake_locations(live_database_client: DatabaseClient):
    # Populate `us_states` with data, returning id
    state_id = live_database_client.create_or_get(
        table_name=Relations.US_STATES.value,
        column_value_mappings=FAKE_STATE_INFO,
    )
    # Populate `counties` with data, returning id
    FAKE_COUNTY_INFO.update({"state_id": state_id})
    county_id = live_database_client.create_or_get(
        table_name=Relations.COUNTIES.value,
        column_value_mappings=FAKE_COUNTY_INFO,
    )
    # Populate `localities` with data, returning id
    FAKE_LOCALITY_INFO.update({"county_id": county_id})
    locality_id = live_database_client.create_or_get(
        table_name=Relations.LOCALITIES.value,
        column_value_mappings=FAKE_LOCALITY_INFO,
    )

    yield FakeLocationsInfo(state_id, county_id, locality_id)

    # After execution, delete rows in `us_states`, `counties`, and `localities`

    live_database_client._delete_from_table(
        table_name=Relations.LOCALITIES.value,
        id_column_value=locality_id,
    )
    live_database_client._delete_from_table(
        table_name=Relations.COUNTIES.value,
        id_column_value=county_id,
    )
    live_database_client._delete_from_table(
        table_name=Relations.US_STATES.value,
        id_column_value=state_id,
    )


def test_locations(
    live_database_client: DatabaseClient, setup_fake_locations: FakeLocationsInfo
):
    """
    Test the following:
        * that if a row in `us_states`, `counties`, or `localities` is created,
            the corresponding row(s) in the `locations` table are also created
        * that if a row in `us_states`, `counties`, or `localities` is deleted,
            the corresponding row(s) in the `locations` table are also deleted
    :param live_database_client:
    :return:
    """
    fake_locations_info = setup_fake_locations

    ID_COLUMN_ARRAY = ["id"]
    # First, validate that all rows are present initially in their respective tables
    results = live_database_client._select_from_single_relation(
        relation_name="us_states",
        columns=ID_COLUMN_ARRAY,
        where_mappings=WhereMapping.from_dict(FAKE_STATE_INFO),
    )
    assert fake_locations_info.state_id == results[0]["id"]

    results = live_database_client._select_from_single_relation(
        relation_name="counties",
        columns=ID_COLUMN_ARRAY,
        where_mappings=WhereMapping.from_dict(FAKE_COUNTY_INFO),
    )
    assert fake_locations_info.county_id == results[0]["id"]

    results = live_database_client._select_from_single_relation(
        relation_name="localities",
        columns=ID_COLUMN_ARRAY,
        where_mappings=WhereMapping.from_dict(FAKE_LOCALITY_INFO),
    )
    assert fake_locations_info.locality_id == results[0]["id"]

    # Assert locations are present in `locations`
    results = live_database_client._select_from_single_relation(
        relation_name="locations",
        columns=["state_id", "county_id", "locality_id"],
        where_mappings=WhereMapping.from_dict({"state_id": fake_locations_info.state_id}),
    )
    assert len(results) == 3
    def any_match(l: list[dict], d: dict):
        for r in l:
            if r == d:
                return True
        return False
    assert any_match(
        results,
        {
            "state_id": fake_locations_info.state_id,
            "county_id": fake_locations_info.county_id,
            "locality_id": fake_locations_info.locality_id,
        }
    )
    assert any_match(
        results,
        {
            "state_id": fake_locations_info.state_id,
            "county_id": fake_locations_info.county_id,
            "locality_id": None,
        }
    )
    assert any_match(
        results,
        {
            "state_id": fake_locations_info.state_id,
            "county_id": None,
            "locality_id": None,
        })


    live_database_client._delete_from_table(
        table_name="localities",
        id_column_value=fake_locations_info.locality_id,
    )

    results = live_database_client._select_from_single_relation(
        relation_name="locations",
        columns=["state_id", "county_id", "locality_id"],
        where_mappings=WhereMapping.from_dict({"state_id": fake_locations_info.state_id}),
    )
    assert len(results) == 2
    assert not any_match(
        results,
        {
            "state_id": fake_locations_info.state_id,
            "county_id": fake_locations_info.county_id,
            "locality_id": fake_locations_info.locality_id,
        }
    )


    live_database_client._delete_from_table(
        table_name="counties",
        id_column_value=fake_locations_info.county_id,
    )

    results = live_database_client._select_from_single_relation(
        relation_name="locations",
        columns=["state_id", "county_id", "locality_id"],
        where_mappings=WhereMapping.from_dict({"state_id": fake_locations_info.state_id}),
    )
    assert len(results) == 1
    assert not any_match(
        results,
        {
            "state_id": fake_locations_info.state_id,
            "county_id": fake_locations_info.county_id,
            "locality_id": None,
        }
    )


    live_database_client._delete_from_table(
        table_name="us_states",
        id_column_value=fake_locations_info.state_id,
    )

    results = live_database_client._select_from_single_relation(
        relation_name="locations",
        columns=["state_id", "county_id", "locality_id"],
        where_mappings=WhereMapping.from_dict({"state_id": fake_locations_info.state_id}),
    )
    assert len(results) == 0