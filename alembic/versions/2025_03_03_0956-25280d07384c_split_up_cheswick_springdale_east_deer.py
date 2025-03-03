"""Split up Cheswick, Springdale, East Deer

Revision ID: 25280d07384c
Revises: fda77b9f39d3
Create Date: 2025-03-03 09:56:04.171379

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from psycopg.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError

# revision identifiers, used by Alembic.
revision: str = "25280d07384c"
down_revision: Union[str, None] = "fda77b9f39d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def execute_and_return(text):
    conn = op.get_bind()
    result = conn.execute(sa.text(text))
    return result.fetchone()


def insert_locality_and_associate_with_agency(locality_name, county_id, agency_id):
    result = execute_and_return(
        f"""
        SELECT ID FROM LOCALITIES WHERE 
        name = '{locality_name}' AND county_id = {county_id}
    """
    )
    if result:
        locality_id = result[0]
    else:
        result = execute_and_return(
            f"""
        INSERT INTO LOCALITIES (name, county_id)
        VALUES ('{locality_name}', {county_id})
        RETURNING id
        """
        )
        locality_id = result[0]

    result = execute_and_return(
        f"""
    SELECT ID FROM LOCATIONS WHERE 
    county_id = {county_id} AND locality_id = {locality_id}
    """
    )

    location_id = result[0]

    op.execute(
        f"""
    INSERT INTO LINK_AGENCIES_LOCATIONS (location_id, agency_id)
    VALUES ({location_id}, {agency_id})
    """
    )


def upgrade() -> None:
    result = execute_and_return(
        """
    SELECT ID, LOCALITY_ID, COUNTY_ID 
    from locations_expanded le
    where le.locality_name = 'Cheswick Springdale East Deer'
    """
    )

    if result is None:
        # Not needed
        return
    location_id, locality_id, county_id = result

    result = execute_and_return(
        f"""
    SELECT AGENCY_ID FROM LINK_AGENCIES_LOCATIONS
    WHERE LOCATION_ID = {location_id}
    """
    )

    agency_id = result[0]

    insert_locality_and_associate_with_agency(
        locality_name="Cheswick", county_id=county_id, agency_id=agency_id
    )
    insert_locality_and_associate_with_agency(
        locality_name="Springdale", county_id=county_id, agency_id=agency_id
    )
    insert_locality_and_associate_with_agency(
        locality_name="East Deer", county_id=county_id, agency_id=agency_id
    )

    op.execute(
        f"""
    DELETE FROM LINK_AGENCIES_LOCATIONS
    WHERE LOCATION_ID = {location_id}
    AND AGENCY_ID = {agency_id}
    """
    )

    op.execute(
        f"""
    DELETE FROM LOCALITIES
    WHERE ID = {locality_id}
    """
    )


def downgrade():
    pass
