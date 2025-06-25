import pytest
from psycopg import IntegrityError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError as IntegrityErrorSA

from db.models.implementations.core.location.core import Location
from db.models.implementations.core.location.county import County
from db.models.implementations.core.location.locality import Locality
from db.models.implementations.core.location.us_state import USState
from middleware.enums import Relations


@pytest.fixture
def pennsylvania_id(live_database_client):
    query = (
        select(Location.id)
        .where(USState.state_name == "Pennsylvania")
        .join(USState, Location.state_id == USState.id)
    )
    return live_database_client.scalar(query)


@pytest.fixture
def allegheny_id(live_database_client):
    query = (
        select(Location.id)
        .where(County.name == "Allegheny")
        .join(County, Location.county_id == County.id)
    )
    return live_database_client.scalar(query)


@pytest.fixture
def pittsburgh_id(live_database_client):
    query = select(County.id).where(County.name == "Allegheny")
    county_id = live_database_client.scalar(query)

    try:
        _ = live_database_client.create_locality(
            table_name=Relations.LOCALITIES.value,
            column_value_mappings={"county_id": county_id, "name": "Pittsburgh"},
        )
    except (IntegrityError, IntegrityErrorSA):
        pass

    query = (
        select(Location.id)
        .where(Locality.name == "Pittsburgh")
        .join(Locality, Location.locality_id == Locality.id)
    )
    return live_database_client.scalar(query)
