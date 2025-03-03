"""Create change_log table and associated logic

Revision ID: 6097f5bfaecd
Revises: 9b4fc9265406
Create Date: 2025-02-17 10:42:59.235505

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = "6097f5bfaecd"
down_revision: Union[str, None] = "9b4fc9265406"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


OperationTypeEnum = sa.Enum("UPDATE", "DELETE", name="operation_type")


def upgrade() -> None:
    # Create change_log table
    op.create_table(
        "change_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("operation_type", OperationTypeEnum, nullable=False),
        sa.Column("table_name", sa.String(), nullable=False),
        sa.Column("affected_id", sa.Integer(), nullable=False),
        sa.Column("old_data", JSONB, nullable=False),
        sa.Column("new_data", JSONB, nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "(operation_type = 'UPDATE' AND old_data IS NOT NULL AND new_data IS NOT NULL) OR "
            "(operation_type = 'DELETE' AND old_data IS NOT NULL AND new_data IS NULL)",
            name="check_update_data_not_null",
        ),
    )
    # create jsonb_diff_val function
    op.execute(
        """
    CREATE OR REPLACE FUNCTION jsonb_diff_val(val1 JSONB,val2 JSONB)
        RETURNS JSONB AS $$
        DECLARE
          result JSONB;
          v RECORD;
        BEGIN
           result = val1;
           FOR v IN SELECT * FROM jsonb_each(val2) LOOP
             IF result @> jsonb_build_object(v.key,v.value)
                THEN result = result - v.key;
             ELSIF result ? v.key THEN CONTINUE;
             ELSE
                result = result || jsonb_build_object(v.key,'null');
             END IF;
           END LOOP;
           RETURN result;
        END;
        $$ LANGUAGE plpgsql;
    """
    )

    # Create log_table_changes trigger function
    op.execute(
        """
    CREATE OR REPLACE FUNCTION log_table_changes()
        RETURNS TRIGGER AS $$
        DECLARE
            old_values JSONB;
            new_values JSONB;
            old_to_new JSONB;
            new_to_old JSONB;
        BEGIN
            -- Identify the changed columns
            old_values = row_to_json(OLD)::jsonb;
        
            -- Handle DELETE operations (store entire OLD row since all data is lost)
            IF (TG_OP = 'DELETE') THEN
                INSERT INTO change_log (operation_type, table_name, affected_id, old_data)
                VALUES ('DELETE', TG_TABLE_NAME, OLD.id, old_values);
                RETURN OLD;
            
            -- Handle UPDATE operations (only log the changed columns)
            ELSIF (TG_OP = 'UPDATE') THEN
                new_values = row_to_json(NEW)::jsonb;
                new_to_old = jsonb_diff_val(old_values, new_values);
                old_to_new = jsonb_diff_val(new_values, old_values);
            
                INSERT INTO change_log (operation_type, table_name, affected_id, old_data, new_data)
                VALUES ('UPDATE', TG_TABLE_NAME, OLD.id, new_to_old, old_to_new);
                RETURN NEW;
            END IF;
        END;
        $$ LANGUAGE plpgsql;
    """
    )

    # Create trigger for tables:
    def create_trigger_query(table_name: str) -> str:
        query = f"""
        CREATE TRIGGER log_{table_name}_changes
        BEFORE UPDATE OR DELETE ON {table_name}
        FOR EACH ROW EXECUTE PROCEDURE log_table_changes();
        """
        op.execute(query)

    # Agencies
    create_trigger_query("agencies")
    # Locations
    create_trigger_query("locations")
    # Localities
    create_trigger_query("localities")
    # Counties
    create_trigger_query("counties")


def downgrade() -> None:
    # Drop log_location_changes trigger function
    op.execute("DROP TRIGGER IF EXISTS log_locations_changes ON public.locations")
    op.execute("DROP TRIGGER IF EXISTS log_agencies_changes ON public.agencies")
    op.execute("DROP TRIGGER IF EXISTS log_localities_changes ON public.localities")
    op.execute("DROP TRIGGER IF EXISTS log_counties_changes ON public.counties")
    # Drop log_table_changes trigger function
    op.execute("DROP FUNCTION IF EXISTS log_table_changes()")
    # Drop jsonb_diff_val function
    op.execute("DROP FUNCTION IF EXISTS jsonb_diff_val()")
    # Drop change_log table
    op.drop_table("change_log")
    # Drop operation type enum
    OperationTypeEnum.drop(op.get_bind())
