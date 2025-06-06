"""Add national location type and instance

Revision ID: 8f26c4cc4c35
Revises: f4773c5636a8
Create Date: 2025-06-06 09:09:53.140499

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from middleware.alembic_helpers import switch_enum_type

# revision identifiers, used by Alembic.
revision: str = "8f26c4cc4c35"
down_revision: Union[str, None] = "f4773c5636a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = "locations"
STATE_ID_COLUMN_NAME = "state_id"
ENUM_NAME = "location_type"
TYPE_COLUMN_NAME = "type"


def drop_views():
    for view in ["recent_searches_expanded", "locations_expanded"]:
        op.execute(f"DROP VIEW IF EXISTS {view}")


def create_views():
    op.execute(
        """
    create view locations_expanded
                    (id, type, state_name, state_iso, county_name, county_fips, locality_name, locality_id, state_id, county_id,
                     display_name, full_display_name)
        as
        SELECT locations.id,
               locations.type,
               us_states.state_name,
               us_states.state_iso,
               counties.name   AS county_name,
               counties.fips   AS county_fips,
               localities.name AS locality_name,
               localities.id   AS locality_id,
               us_states.id    AS state_id,
               counties.id     AS county_id,
               CASE
                   WHEN locations.type = 'Locality'::location_type THEN localities.name
                   WHEN locations.type = 'County'::location_type THEN counties.name::character varying
                   WHEN locations.type = 'State'::location_type THEN us_states.state_name::character varying
                   ELSE NULL::character varying
                   END         AS display_name,
               CASE
                   WHEN locations.type = 'Locality'::location_type THEN concat(localities.name, ', ', counties.name, ', ',
                                                                               us_states.state_name)::character varying
                   WHEN locations.type = 'County'::location_type
                       THEN concat(counties.name, ', ', us_states.state_name)::character varying
                   WHEN locations.type = 'State'::location_type THEN us_states.state_name::character varying
                   ELSE NULL::character varying
                   END         AS full_display_name
        FROM locations
                 LEFT JOIN us_states ON locations.state_id = us_states.id
                 LEFT JOIN counties ON locations.county_id = counties.id
                 LEFT JOIN localities ON locations.locality_id = localities.id
            
    """
    )

    op.execute(
        """
    create view recent_searches_expanded
            (id, user_id, location_id, county_name, locality_name, location_type, record_categories, state_name) as
SELECT rs.id,
       rs.user_id,
       rs.location_id,
       le.county_name,
       le.locality_name,
       le.type            AS location_type,
       array_agg(rc.name) AS record_categories,
       le.state_name
FROM recent_searches rs
         JOIN locations_expanded le ON rs.location_id = le.id
         JOIN link_recent_search_record_categories link ON link.recent_search_id = rs.id
         JOIN record_categories rc ON link.record_category_id = rc.id
GROUP BY le.county_name, le.locality_name, le.type, le.state_name, rs.id;
    """
    )


def drop_materialized_views():
    for materialized_view in [
        "map_counties",
        "map_states",
        "map_localities",
        "typeahead_locations",
        "typeahead_agencies",
    ]:
        op.execute(f"DROP MATERIALIZED VIEW IF EXISTS {materialized_view}")


def create_materialized_views():
    op.execute(
        """
        create materialized view map_counties as
            WITH all_county_locations AS (SELECT lp.id AS county_location_id,
                                                 dp.dependent_location_id
                                          FROM locations lp
                                                   LEFT JOIN dependent_locations dp ON lp.id = dp.parent_location_id
                                          WHERE lp.type = 'County'::location_type
                                          UNION ALL
                                          SELECT locations.id AS county_location_id,
                                                 locations.id AS dependent_location_id
                                          FROM locations
                                          WHERE locations.type = 'County'::location_type)
            SELECT c.name                             AS county_name,
                   c.fips,
                   s.state_iso,
                   acl.county_location_id             AS location_id,
                   count(DISTINCT las.data_source_id) AS data_source_count
            FROM all_county_locations acl
                     JOIN counties c ON c.id = ((SELECT locations.county_id
                                                 FROM locations
                                                 WHERE locations.id = acl.county_location_id))
                     JOIN us_states s ON s.id = c.state_id
                     LEFT JOIN link_agencies_locations lal ON lal.location_id = acl.dependent_location_id
                     LEFT JOIN link_agencies_data_sources las ON las.agency_id = lal.agency_id
            GROUP BY c.name, c.fips, s.state_iso, acl.county_location_id
    """
    )

    op.execute(
        """
    create materialized view map_states as
        WITH all_state_locations AS (SELECT lp.id AS state_location_id,
                                            dp.dependent_location_id
                                     FROM locations lp
                                              LEFT JOIN dependent_locations dp ON lp.id = dp.parent_location_id
                                     WHERE lp.type = 'State'::location_type
                                     UNION ALL
                                     SELECT locations.id AS state_location_id,
                                            locations.id AS dependent_location_id
                                     FROM locations
                                     WHERE locations.type = 'State'::location_type)
        SELECT s.state_name,
               s.state_iso,
               asl.state_location_id              AS location_id,
               count(DISTINCT las.data_source_id) AS data_source_count
        FROM all_state_locations asl
                 JOIN us_states s ON s.id = ((SELECT locations.state_id
                                              FROM locations
                                              WHERE locations.id = asl.state_location_id))
                 LEFT JOIN link_agencies_locations lal ON lal.location_id = asl.dependent_location_id
                 LEFT JOIN link_agencies_data_sources las ON las.agency_id = lal.agency_id
        GROUP BY s.state_name, s.state_iso, asl.state_location_id;
    """
    )

    op.execute(
        """
    create materialized view typeahead_agencies as
        SELECT a.id,
               a.name,
               a.jurisdiction_type,
               l.state_iso,
               l.locality_name AS municipality,
               l.county_name
        FROM agencies a
                 LEFT JOIN link_agencies_locations lal ON lal.agency_id = a.id
                 LEFT JOIN locations_expanded l ON lal.location_id = l.id
        WHERE a.approval_status = 'approved'::approval_status;
    """
    )

    op.execute(
        """
    create materialized view typeahead_locations as
        SELECT le.id   AS location_id,
               CASE
                   WHEN le.type = 'Locality'::location_type THEN le.locality_name
                   WHEN le.type = 'County'::location_type THEN le.county_name::character varying
                   WHEN le.type = 'State'::location_type THEN le.state_name::character varying
                   ELSE NULL::character varying
                   END AS search_name,
               CASE
                   WHEN le.type = 'Locality'::location_type
                       THEN concat(le.locality_name, ', ', le.county_name, ', ', le.state_name)::character varying
                   WHEN le.type = 'County'::location_type THEN concat(le.county_name, ', ', le.state_name)::character varying
                   WHEN le.type = 'State'::location_type THEN le.state_name::character varying
                   ELSE NULL::character varying
                   END AS display_name,
               le.type,
               le.state_name,
               le.county_name,
               le.locality_name
        FROM locations_expanded le
"""
    )

    op.execute(
        """
    CREATE MATERIALIZED VIEW map_localities AS
    SELECT 
        loc.name AS locality_name,
        c.name AS county_name,
        l.lat,
        l.lng,
        l.id AS location_id,
        c.fips as county_fips,
        s.state_iso,
        COUNT(DISTINCT las.data_source_id) AS data_source_count
    FROM public.localities loc
    JOIN public.counties c 
        ON loc.county_id = c.id
    JOIN public.us_states s 
        ON c.state_id = s.id
    JOIN public.locations l 
        ON l.locality_id = loc.id AND l.type = 'Locality'
    LEFT JOIN public.link_agencies_locations lal 
        ON lal.location_id = l.id
    LEFT JOIN public.link_agencies_data_sources las 
        ON las.agency_id = lal.agency_id
    WHERE l.LAT IS NOT NULL AND l.LNG IS NOT NULL
    GROUP BY loc.name, c.name, l.lat, l.lng, l.id, c.fips, s.state_iso;
    """
    )


def upgrade() -> None:
    # Drop not null constraint on `state_id` column
    op.alter_column(TABLE_NAME, STATE_ID_COLUMN_NAME, nullable=True)

    # Drop views
    drop_materialized_views()
    drop_views()

    # Drop dependent locations view
    op.execute("DROP VIEW IF EXISTS dependent_locations")

    # Drop prior `locations_check` constraint
    op.execute(
        f"""
    ALTER TABLE {TABLE_NAME} DROP CONSTRAINT locations_check;
    """
    )

    # Add new `National` location type
    switch_enum_type(
        table_name=TABLE_NAME,
        column_name=TYPE_COLUMN_NAME,
        enum_name=ENUM_NAME,
        new_enum_values=["State", "County", "Locality", "National"],
        mapping_dict={"State": "State", "County": "County", "Locality": "Locality"},
    )

    # Add new `locations_check` constraint
    op.execute(
        f"""
    ALTER TABLE {TABLE_NAME} ADD CONSTRAINT locations_check
    CHECK 
        (
            ((type = 'National'::location_type) AND (state_id IS NULL) AND (county_id IS NULL) AND (locality_id IS NULL)) OR
            ((type = 'State'::location_type) AND (county_id IS NULL) AND (locality_id IS NULL)) OR
            ((type = 'County'::location_type) AND (county_id IS NOT NULL) AND (locality_id IS NULL)) OR
            ((type = 'Locality'::location_type) AND (county_id IS NOT NULL) AND (locality_id IS NOT NULL))
        )
    ;
    """
    )

    # Add dependent locations view
    op.execute(
        """
    create view dependent_locations(parent_location_id, dependent_location_id) as
        SELECT lp.id AS parent_location_id,
               ld.id AS dependent_location_id
        FROM locations lp
                 JOIN locations ld 
                      ON ld.state_id = lp.state_id 
                          AND ld.type = 'County'::location_type 
                          AND lp.type = 'State'::location_type
        UNION ALL
        SELECT lp.id AS parent_location_id,
               ld.id AS dependent_location_id
        FROM locations lp
                 JOIN locations ld 
                      ON ld.county_id = lp.county_id 
                          AND ld.type = 'Locality'::location_type 
                          AND lp.type = 'County'::location_type
        UNION ALL
        SELECT lp.id AS parent_location_id,
               ld.id AS dependent_location_id
        FROM locations lp
                 JOIN locations ld
                      ON ld.state_id = lp.state_id 
                          AND ld.type = 'Locality'::location_type 
                          AND lp.type = 'State'::location_type
        UNION ALL
        SELECT lp.id AS parent_location_id,
               ld.id AS dependent_location_id
        FROM locations lp
                 JOIN locations ld
                      ON lp.type = 'National'::location_type
                         AND ld.type IN (
                                         'State'::location_type, 
                                         'County'::location_type, 
                                         'Locality'::location_type
                              );
    """
    )

    # Create materialized views
    create_views()
    create_materialized_views()

    # Add national location instance
    op.execute(
        """
    INSERT INTO locations (type, state_id, county_id, locality_id) 
    VALUES ('National', null, null, null);
    """
    )


def downgrade() -> None:
    # Remove national location instance
    op.execute(
        """
    DELETE FROM locations WHERE type = 'National';
    """
    )

    # Add not null constraint on `state_id` column
    op.alter_column(TABLE_NAME, STATE_ID_COLUMN_NAME, nullable=False)

    # Drop prior `locations_check` constraint
    op.execute(
        f"""
    ALTER TABLE {TABLE_NAME} DROP CONSTRAINT locations_check;
    """
    )

    # Drop views
    drop_materialized_views()
    drop_views()

    # Drop dependent locations view
    op.execute("DROP VIEW IF EXISTS dependent_locations")

    switch_enum_type(
        table_name=TABLE_NAME,
        column_name=TYPE_COLUMN_NAME,
        enum_name=ENUM_NAME,
        new_enum_values=["State", "County", "Locality"],
    )

    # Add new `locations_check` constraint
    op.execute(
        f"""
    ALTER TABLE {TABLE_NAME} ADD CONSTRAINT locations_check
    CHECK 
        (
            ((type = 'State'::location_type) AND (county_id IS NULL) AND (locality_id IS NULL)) OR
            ((type = 'County'::location_type) AND (county_id IS NOT NULL) AND (locality_id IS NULL)) OR
            ((type = 'Locality'::location_type) AND (county_id IS NOT NULL) AND (locality_id IS NOT NULL))
        )
    ;
    """
    )

    # Add dependent locations view
    op.execute(
        """
    create view dependent_locations(parent_location_id, dependent_location_id) as
        SELECT lp.id AS parent_location_id,
               ld.id AS dependent_location_id
        FROM locations lp
                 JOIN locations ld ON ld.state_id = lp.state_id AND ld.type = 'County'::location_type AND lp.type = 'State'::location_type
        UNION ALL
        SELECT lp.id AS parent_location_id,
               ld.id AS dependent_location_id
        FROM locations lp
                 JOIN locations ld ON ld.county_id = lp.county_id AND ld.type = 'Locality'::location_type AND lp.type = 'County'::location_type
        UNION ALL
        SELECT lp.id AS parent_location_id,
               ld.id AS dependent_location_id
        FROM locations lp
                 JOIN locations ld
                      ON ld.state_id = lp.state_id AND ld.type = 'Locality'::location_type AND lp.type = 'State'::location_type;
    """
    )

    # Create views
    create_views()
    create_materialized_views()
