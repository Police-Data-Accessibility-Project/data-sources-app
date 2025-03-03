"""Remove agencies.name and make submitted_name new name column

Revision ID: 8ba99f12446d
Revises: 12cf56cbebb7
Create Date: 2025-02-06 09:06:46.556363

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import String, Column

# revision identifiers, used by Alembic.
revision: str = "8ba99f12446d"
down_revision: Union[str, None] = "12cf56cbebb7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

CREATE_MATERIALIZED_VIEW_SCRIPT = """
    CREATE MATERIALIZED VIEW IF NOT EXISTS public.typeahead_agencies
    TABLESPACE pg_default
    AS
     SELECT a.id,
        a.name,
        a.jurisdiction_type,
        l.state_iso,
        l.locality_name AS municipality,
        l.county_name
       FROM agencies a
         LEFT JOIN locations_expanded l ON a.location_id = l.id
    WITH DATA;
"""
DROP_VIEW_SCRIPT = "DROP VIEW public.agencies_expanded;"
DROP_MATERIALIZED_VIEW_SCRIPT = "DROP MATERIALIZED VIEW public.typeahead_agencies;"


def upgrade() -> None:
    op.execute(DROP_VIEW_SCRIPT)
    op.execute(DROP_MATERIALIZED_VIEW_SCRIPT)
    op.drop_column(table_name="agencies", column_name="name")
    op.execute(
        """
    DROP TRIGGER IF EXISTS trigger_set_agency_name ON public.agencies;
    DROP FUNCTION IF EXISTS set_agency_name();
    COMMIT;
    """
    )
    op.alter_column(
        table_name="agencies", column_name="submitted_name", new_column_name="name"
    )
    op.execute(
        """
    CREATE OR REPLACE VIEW public.agencies_expanded
     AS
     SELECT a.name,
        a.name as submitted_name,
        a.homepage_url,
        a.jurisdiction_type,
        l.state_iso,
        l.state_name,
        l.county_fips,
        l.county_name,
        a.lat,
        a.lng,
        a.defunct_year,
        a.id,
        a.agency_type,
        a.multi_agency,
        a.zip_code,
        a.no_web_presence,
        a.airtable_agency_last_modified,
        a.approved,
        a.rejection_reason,
        a.last_approval_editor,
        a.submitter_contact,
        a.agency_created,
        l.locality_name
       FROM agencies a
         LEFT JOIN locations_expanded l ON a.location_id = l.id;
    COMMENT ON VIEW public.agencies_expanded
        IS 'View containing information about agencies as well as limited information from other tables connected by foreign keys.';
    """
    )
    op.execute(CREATE_MATERIALIZED_VIEW_SCRIPT)

    op.execute(
        """
    WITH agency_rc_id AS(
    
        SELECT rc.id
        FROM relation_column rc
        WHERE rc.relation = 'agencies'
        AND rc.associated_column = 'name'
    
    )
    
    UPDATE COLUMN_PERMISSION CP
    SET ACCESS_PERMISSION = 'WRITE'
    WHERE CP.RC_ID IN (SELECT ID FROM agency_rc_id) AND CP.RELATION_ROLE = 'ADMIN';
    """
    )


def downgrade() -> None:
    op.execute(DROP_VIEW_SCRIPT)
    op.execute(DROP_MATERIALIZED_VIEW_SCRIPT)
    op.alter_column(
        table_name="agencies", column_name="name", new_column_name="submitted_name"
    )
    op.add_column(table_name="agencies", column=Column(name="name", type_=String()))
    op.execute(
        """
        CREATE OR REPLACE FUNCTION public.set_agency_name()
        RETURNS trigger
        LANGUAGE 'plpgsql'
        COST 100
        VOLATILE NOT LEAKPROOF
    AS $BODY$
    BEGIN
        IF NEW.submitted_name IS NOT NULL THEN
            IF NEW.state_iso IS NOT NULL THEN
                NEW.name := NEW.submitted_name || ' - ' || NEW.state_iso;
            ELSE
                NEW.name := NEW.submitted_name;
            END IF;
        END IF;
    
        RETURN NEW;
    END;
    $BODY$;
    
    COMMENT ON FUNCTION public.set_agency_name()
    IS 'Updates `name` based on contents of `submitted_name` and `state_iso`';
    """
    )

    op.execute(
        """
    CREATE OR REPLACE TRIGGER trigger_set_agency_name
    BEFORE INSERT OR UPDATE 
    ON public.agencies
    FOR EACH ROW
    EXECUTE FUNCTION public.set_agency_name();

    COMMENT ON TRIGGER trigger_set_agency_name ON public.agencies
        IS 'Calls `set_agency_name()` on inserts or updates to an Agency Row';
    """
    )

    op.execute(
        """
    CREATE OR REPLACE VIEW public.agencies_expanded
     AS
     SELECT a.name,
        a.submitted_name,
        a.homepage_url,
        a.jurisdiction_type,
        l.state_iso,
        l.state_name,
        l.county_fips,
        l.county_name,
        a.lat,
        a.lng,
        a.defunct_year,
        a.id,
        a.agency_type,
        a.multi_agency,
        a.zip_code,
        a.no_web_presence,
        a.airtable_agency_last_modified,
        a.approved,
        a.rejection_reason,
        a.last_approval_editor,
        a.submitter_contact,
        a.agency_created,
        l.locality_name
       FROM agencies a
         LEFT JOIN locations_expanded l ON a.location_id = l.id;
         
     COMMENT ON VIEW public.agencies_expanded
        IS 'View containing information about agencies as well as limited information from other tables connected by foreign keys.';
     """
    )
    op.execute(
        """
    CREATE MATERIALIZED VIEW IF NOT EXISTS public.typeahead_agencies
    TABLESPACE pg_default
    AS
     SELECT a.id,
        a.name,
        a.jurisdiction_type,
        l.state_iso,
        l.locality_name AS municipality,
        l.county_name
       FROM agencies a
         LEFT JOIN locations_expanded l ON a.location_id = l.id
    WITH DATA;
    """
    )

    op.execute(
        """
    WITH agency_rc_id AS(

    SELECT rc.id
    FROM relation_column rc
    WHERE rc.relation = 'agencies'
    AND rc.associated_column = 'name'

    )

    UPDATE COLUMN_PERMISSION CP
    SET ACCESS_PERMISSION = 'READ'
    WHERE CP.RC_ID IN (SELECT ID FROM agency_rc_id) AND CP.RELATION_ROLE = 'ADMIN';
    """
    )
