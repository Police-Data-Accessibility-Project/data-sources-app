import sqlalchemy as sa
from alembic import op


def switch_enum_type(
    table_name,
    column_name,
    enum_name,
    new_enum_values,
    drop_old_enum=True,
    mapping_dict=None,
):
    """
    Switches an ENUM type in a PostgreSQL column by:
    1. Renaming the old enum type.
    2. Creating the new enum type with the same name.
    3. Updating the column to use the new enum type.
    4. Dropping the old enum type.

    :param table_name: Name of the table containing the ENUM column.
    :param column_name: Name of the column using the ENUM type.
    :param enum_name: Name of the ENUM type in PostgreSQL.
    :param new_enum_values: List of new ENUM values.
    :param drop_old_enum: Whether to drop the old ENUM type.
    :param mapping_dict: Optional dict mapping old values to new values.
    """
    conn = op.get_bind()

    # Ensure names are safely quoted
    quoted_table_name = f'"{table_name}"'
    quoted_column_name = f'"{column_name}"'
    quoted_enum_name = f'"{enum_name}"'

    # Step 1: Rename the old ENUM type
    old_enum_temp_name = f"{enum_name}_old"
    quoted_old_enum_name = f'"{old_enum_temp_name}"'
    op.execute(
        sa.text(f"ALTER TYPE {quoted_enum_name} RENAME TO {quoted_old_enum_name}")
    )

    # Step 2: Create the new ENUM type safely
    new_enum_type = sa.Enum(*new_enum_values, name=enum_name)
    new_enum_type.create(conn)

    # Step 3: Ensure existing values are compatible with the new enum
    query = f"SELECT DISTINCT {quoted_column_name} FROM {quoted_table_name}"  # nosec
    existing_values = [row[0] for row in conn.execute(sa.text(query)).fetchall()]

    # Build the mapping of final target values:
    if mapping_dict:
        mapped_values = [mapping_dict.get(val, val) for val in existing_values]
    else:
        mapped_values = existing_values

    # Validate that all mapped values are in the new enum:
    invalid_values = [val for val in mapped_values if val not in new_enum_values]
    if invalid_values:
        raise ValueError(
            f"Existing column '{column_name}' contains invalid mapped values: {invalid_values}"
        )

    # Step 4: Change column type using explicit cast or CASE
    if mapping_dict:
        # Build explicit CASE WHEN statement
        case_clauses = "\n".join(
            f"WHEN '{old_val}' THEN '{new_val}'::{quoted_enum_name}"
            for old_val, new_val in mapping_dict.items()
        )
        using_expr = f"""
            CASE ({quoted_column_name}::text)
                {case_clauses}
                ELSE ({quoted_column_name}::text):: {quoted_enum_name}
            END
        """
    else:
        # Default text cast if no mapping provided
        using_expr = f"{quoted_column_name}::text::{quoted_enum_name}"

    op.execute(
        sa.text(
            f"""
            ALTER TABLE {quoted_table_name} 
            ALTER COLUMN {quoted_column_name} 
            SET DATA TYPE {quoted_enum_name} 
            USING {using_expr}
            """
        )
    )

    # Step 5: Drop the old ENUM type if required
    if drop_old_enum:
        op.execute(sa.text(f"DROP TYPE {quoted_old_enum_name}"))


def add_permission(permission_name, description):
    op.execute(
        sa.text(
            """
        INSERT INTO permissions (permission_name, description)
        VALUES (:permission_name, :description)"""
        ).bindparams(permission_name=permission_name, description=description)
    )


def remove_permission(permission_name):
    op.execute(
        sa.text(
            """
        DELETE FROM permissions WHERE permission_name = :permission_name"""
        ).bindparams(permission_name=permission_name)
    )


def id_column():
    return sa.Column("id", sa.Integer, primary_key=True, nullable=False)


def agency_id_column():
    return sa.Column(
        "agency_id",
        sa.Integer,
        sa.ForeignKey("agencies.id", ondelete="CASCADE"),
        nullable=False,
    )


def user_id_column():
    return sa.Column(
        "user_id",
        sa.Integer,
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )


def record_type_id_column():
    return sa.Column(
        "record_type_id",
        sa.Integer,
        sa.ForeignKey("record_types.id", ondelete="CASCADE"),
        nullable=False,
    )


def updated_at_column():
    return sa.Column(
        "updated_at",
        sa.DateTime,
        server_default=sa.func.now(),
        server_onupdate=sa.func.now(),
        nullable=False,
    )


def created_at_column():
    return sa.Column(
        "created_at", sa.DateTime, server_default=sa.func.now(), nullable=False
    )


def enum_column(
    column_name: str, enum_name: str, enum_values: list[str], nullable: bool = False
):
    return sa.Column(
        column_name,
        sa.Enum(*enum_values, name=enum_name),
        nullable=nullable,
    )


def list_of_enums_column(
    column_name: str, enum_name: str, enum_values: list[str], nullable: bool = False
):
    return sa.Column(
        column_name,
        sa.ARRAY(sa.Enum(*enum_values, name=enum_name)),
        nullable=nullable,
    )


def drop_enum(enum_name: str) -> None:
    enum = sa.Enum(name=enum_name)
    enum.drop(op.get_bind())
