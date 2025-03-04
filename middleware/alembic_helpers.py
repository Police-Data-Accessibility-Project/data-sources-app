from alembic import op
import sqlalchemy as sa

import sqlalchemy as sa
from alembic import op


def switch_enum_type(
    table_name, column_name, enum_name, new_enum_values, drop_old_enum=True
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
    """
    conn = op.get_bind()

    # Step 1: Rename the old ENUM type
    old_enum_temp_name = f"{enum_name}_old"
    op.execute(f'ALTER TYPE "{enum_name}" RENAME TO "{old_enum_temp_name}"')

    # Step 2: Create the new ENUM type
    new_enum_type = sa.Enum(*new_enum_values, name=enum_name)
    new_enum_type.create(conn)

    # Step 3: Ensure existing values are compatible with the new enum
    existing_values = [
        row[0]
        for row in conn.execute(
            sa.text(f'SELECT DISTINCT "{column_name}" FROM "{table_name}"')
        ).fetchall()
    ]

    invalid_values = [val for val in existing_values if val not in new_enum_values]
    if invalid_values:
        raise ValueError(
            f"Existing column '{column_name}' contains invalid values: {invalid_values}"
        )

    # Step 4: Change column type (explicit cast)
    op.execute(
        f"""
        ALTER TABLE "{table_name}" 
        ALTER COLUMN "{column_name}" 
        SET DATA TYPE "{enum_name}" 
        USING "{column_name}"::text::{enum_name}
    """
    )

    # Step 5: Drop the old ENUM type
    if drop_old_enum:
        op.execute(f'DROP TYPE "{old_enum_temp_name}"')
