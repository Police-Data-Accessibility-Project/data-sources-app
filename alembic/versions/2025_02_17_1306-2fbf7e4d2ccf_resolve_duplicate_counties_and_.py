"""Resolve duplicate counties and localities for same state

Revision ID: 2fbf7e4d2ccf
Revises: 6097f5bfaecd
Create Date: 2025-02-17 13:06:06.522172

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2fbf7e4d2ccf"
down_revision: Union[str, None] = "6097f5bfaecd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def execute_query(fips, locality_name, county_type) -> None:
    with_query = f"""
            WITH 
            county_info as (
                SELECT COUNTY_ID, ID AS county_location_id
                FROM LOCATIONS_EXPANDED
                WHERE type = 'County' and county_fips = '{fips}'
            ),
            locality_info as (
                SELECT LOCALITY_ID, ID AS locality_location_id
                FROM LOCATIONS_EXPANDED
                WHERE type = 'Locality' 
                and county_fips = '{fips}' 
                and locality_name = '{locality_name}'
            )
    """
    query = f"""
        
        {with_query}
        -- Change county name
        UPDATE COUNTIES
        SET name = concat(name, ' ', '{county_type}')
        FROM county_info
        WHERE ID = county_info.county_id;
        
        {with_query}
        -- Change Locality Location to county location
        UPDATE AGENCIES
        SET LOCATION_ID = county_info.county_location_id
        from county_info, locality_info
        WHERE LOCATION_ID = locality_info.locality_location_id;
        
        {with_query}
        UPDATE LINK_LOCATIONS_DATA_REQUESTS
        SET LOCATION_ID = county_info.county_location_id
        from county_info, locality_info
        WHERE LOCATION_ID = locality_info.locality_location_id;
        
        -- Link_user_followed_location should have no users, so this can be ignored
        
        {with_query}
        DELETE FROM LOCALITIES
        USING locality_info
        where id = locality_info.locality_id;
        
        {with_query}
        DELETE FROM LOCATIONS
        USING locality_info
        WHERE id = locality_info.locality_location_id;
    """

    op.execute(query)


def upgrade() -> None:
    for fips, county_type, locality_name in [
        ["24510", "City", "Baltimore"],
        ["24005", "County", "Baltimore"],
        ["51600", "City", "Fairfax"],
        ["51059", "County", "Fairfax"],
        ["51620", "City", "Franklin"],
        ["51067", "County", "Franklin"],
        ["51159", "County", "Richmond"],
        ["51760", "City", "Richmond"],
        ["51161", "County", "Roanoke"],
        ["51770", "City", "Roanoke"],
        ["29189", "County", "St. Louis"],
        ["29510", "City", "St. Louis"],
        ["29189", "County", "Saint Louis"],
        ["29510", "City", "Saint Louis"],
    ]:
        execute_query(fips=fips, locality_name=locality_name, county_type=county_type)


def downgrade() -> None:
    # This migration cannot be reversed
    pass
