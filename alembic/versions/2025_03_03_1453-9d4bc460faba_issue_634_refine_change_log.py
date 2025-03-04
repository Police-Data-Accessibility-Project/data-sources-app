"""Issue 634 - Refine change_log

Revision ID: 9d4bc460faba
Revises: 25280d07384c
Create Date: 2025-03-03 14:53:20.479268

"""

from typing import Sequence, Union

from alembic import op

from middleware.alembic_helpers import switch_enum_type

# revision identifiers, used by Alembic.
revision: str = "9d4bc460faba"
down_revision: Union[str, None] = "25280d07384c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass
    op.execute(
        """
        CREATE OR REPLACE FUNCTION public.log_table_changes()
        RETURNS trigger
        LANGUAGE 'plpgsql'
        COST 100
        VOLATILE NOT LEAKPROOF
    AS $BODY$
            DECLARE
                old_values JSONB;
                new_values JSONB;
                old_to_new JSONB;
                new_to_old JSONB;
            BEGIN
                -- Handle DELETE operations (store entire OLD row since all data is lost)
                IF (TG_OP = 'DELETE') THEN
                    old_values = row_to_json(OLD)::jsonb;

                    INSERT INTO change_log (operation_type, table_name, affected_id, old_data)
                    VALUES ('DELETE', TG_TABLE_NAME, OLD.id, old_values);

                    RETURN OLD;

                -- Handle UPDATE operations (only log the changed columns)
                ELSIF (TG_OP = 'UPDATE') THEN
                    old_values = row_to_json(OLD)::jsonb;
                    new_values = row_to_json(NEW)::jsonb;
                    new_to_old = jsonb_diff_val(old_values, new_values);
                    old_to_new = jsonb_diff_val(new_values, old_values);

                    -- Skip logging if both old_to_new and new_to_old are NULL or empty JSON objects
                    IF (new_to_old IS NOT NULL AND new_to_old <> '{}') OR
                       (old_to_new IS NOT NULL AND old_to_new <> '{}') THEN
                        INSERT INTO change_log (operation_type, table_name, affected_id, old_data, new_data)
                        VALUES ('UPDATE', TG_TABLE_NAME, OLD.id, new_to_old, old_to_new);
                    END IF;

                    RETURN NEW;

                -- Handle INSERT operations
                ELSIF (TG_OP = 'INSERT') THEN
                    new_values = row_to_json(NEW)::jsonb;

                    -- Skip logging if new_values is NULL or an empty JSON object
                    IF new_values IS NOT NULL AND new_values <> '{}' THEN
                        INSERT INTO change_log (operation_type, table_name, affected_id, new_data)
                        VALUES ('INSERT', TG_TABLE_NAME, NEW.id, new_values);
                    END IF;

                    RETURN NEW;
                END IF;
            END;
    $BODY$;
    """
    )

    def create_table_trigger(table_name: str) -> None:
        op.execute(
            """
        CREATE OR REPLACE TRIGGER log_{table_name}_changes
        BEFORE INSERT OR DELETE OR UPDATE
        ON public.{table_name}
        FOR EACH ROW
        EXECUTE FUNCTION public.log_table_changes();
        """.format(
                table_name=table_name
            )
        )

    for table in [
        "agencies",
        "locations",
        "counties",
        "data_sources",
        "link_agencies_locations",
        "localities",
        "users",
    ]:
        create_table_trigger(table)

    op.execute(
        """
    DELETE FROM CHANGE_LOG
    where old_data = '{}'::jsonb and new_data = '{}'::jsonb
    """
    )

    # Drop constraint 'check_update_data_not_null'
    op.execute(
        """
    ALTER TABLE change_log
    DROP CONSTRAINT check_update_data_not_null
    """
    )

    switch_enum_type(
        "change_log",
        column_name="operation_type",
        enum_name="operation_type",
        new_enum_values=["INSERT", "UPDATE", "DELETE"],
    )

    # Drop not null constraint for `old_data`
    op.alter_column(
        table_name="change_log",
        column_name="old_data",
        nullable=True,
    )


def downgrade() -> None:
    pass
    op.execute(
        """
        CREATE OR REPLACE FUNCTION public.log_table_changes()
        RETURNS trigger
        LANGUAGE 'plpgsql'
        COST 100
        VOLATILE NOT LEAKPROOF
    AS $BODY$
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
                -- Handle UPDATE operations nly log the changed columns)
                ELSIF (TG_OP = 'UPDATE') THEN
                    new_values = row_to_json(NEW)::jsonb;
                    new_to_old = jsonb_diff_val(old_values, new_values);
                    old_to_new = jsonb_diff_val(new_values, old_values);

                    INSERT INTO change_log (operation_type, table_name, affected_id, old_data, new_data)
                    VALUES ('UPDATE', TG_TABLE_NAME, OLD.id, new_to_old, old_to_new);
                    RETURN NEW;
                END IF;
            END;

    $BODY$;

    """
    )

    def create_table_trigger(table_name: str) -> None:
        op.execute(
            """
        CREATE OR REPLACE TRIGGER log_{table_name}_changes
        BEFORE INSERT OR DELETE
        ON public.{table_name}
        FOR EACH ROW
        EXECUTE FUNCTION public.log_table_changes();
        """.format(
                table_name=table_name
            )
        )

    for table in [
        "agencies",
        "locations",
        "counties",
        "data_sources",
        "link_agencies_locations",
        "localities",
    ]:
        create_table_trigger(table)

    op.execute("DROP TRIGGER IF EXISTS log_users_changes ON public.users")

    op.execute(
        """
    DELETE FROM CHANGE_LOG
    WHERE operation_type = 'INSERT'
    """
    )

    switch_enum_type(
        "change_log",
        column_name="operation_type",
        enum_name="operation_type",
        new_enum_values=["UPDATE", "DELETE"],
    )

    op.create_check_constraint(
        "check_update_data_not_null",
        "change_log",
        "(operation_type = 'UPDATE' AND old_data IS NOT NULL AND new_data IS NOT NULL) OR "
        "(operation_type = 'DELETE' AND old_data IS NOT NULL AND new_data IS NULL)",
    )

    op.alter_column(
        table_name="change_log",
        column_name="old_data",
        nullable=False,
    )
