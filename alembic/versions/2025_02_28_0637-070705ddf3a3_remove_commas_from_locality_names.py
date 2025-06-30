"""Remove commas from locality names

Revision ID: 070705ddf3a3
Revises: 9ff5381647ed
Create Date: 2025-02-28 06:37:06.220363

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "070705ddf3a3"
down_revision: Union[str, None] = "9ff5381647ed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def address_duplicate(
    true_location_id: int, duplicate_location_id: int, duplicate_locality_id: int
):
    op.execute(
        """
    UPDATE AGENCIES
    SET location_id = {true_location_id}
    WHERE location_id = {duplicate_location_id}
    """.format(
            true_location_id=true_location_id,
            duplicate_location_id=duplicate_location_id,
        )
    )
    op.execute(
        """
    DELETE FROM LOCALITIES
    WHERE ID = {duplicate_locality_id}
    """.format(duplicate_locality_id=duplicate_locality_id)
    )


def upgrade() -> None:
    # Address duplicates
    # Jenks, Oklahoma
    address_duplicate(
        true_location_id=8965, duplicate_location_id=3861, duplicate_locality_id=663
    )
    # Potaeu, Oklahoma
    address_duplicate(
        true_location_id=14772, duplicate_location_id=4699, duplicate_locality_id=1501
    )
    # Catoosa, Oklahoma
    address_duplicate(
        true_location_id=13617, duplicate_location_id=4814, duplicate_locality_id=1616
    )
    # Wilburton, Oklahoma
    address_duplicate(
        true_location_id=7673, duplicate_location_id=5868, duplicate_locality_id=2670
    )
    # Madill, Oklahoma
    address_duplicate(
        true_location_id=12630, duplicate_location_id=6479, duplicate_locality_id=3281
    )
    # Tahlequah, Oklahoma
    address_duplicate(
        true_location_id=13683, duplicate_location_id=6574, duplicate_locality_id=3376
    )
    # Norman, Oklahoma
    address_duplicate(
        true_location_id=13424, duplicate_location_id=7288, duplicate_locality_id=4090
    )
    # Tulsa, Oklahoma
    address_duplicate(
        true_location_id=3989, duplicate_location_id=7861, duplicate_locality_id=4663
    )
    # Lawton, Oklahoma
    address_duplicate(
        true_location_id=11014, duplicate_location_id=8074, duplicate_locality_id=4876
    )
    # Noble, Oklahoma
    address_duplicate(
        true_location_id=10931, duplicate_location_id=8154, duplicate_locality_id=4956
    )
    # Montgomery, Alabama
    address_duplicate(
        true_location_id=5754, duplicate_location_id=9603, duplicate_locality_id=6405
    )
    # Beggs, Oklahoma
    address_duplicate(
        true_location_id=3506, duplicate_location_id=10385, duplicate_locality_id=7187
    )
    # Stillwater, Oklahoma
    address_duplicate(
        true_location_id=5475, duplicate_location_id=10510, duplicate_locality_id=7312
    )
    # Altus, Oklahoma
    address_duplicate(
        true_location_id=5500, duplicate_location_id=11656, duplicate_locality_id=8458
    )
    # Lone Wolf, Oklahoma
    address_duplicate(
        true_location_id=13751, duplicate_location_id=12554, duplicate_locality_id=9356
    )
    # Muskogee, Oklahoma
    address_duplicate(
        true_location_id=8844, duplicate_location_id=12642, duplicate_locality_id=9444
    )
    # Edmond, Oklahoma
    address_duplicate(
        true_location_id=4893, duplicate_location_id=13696, duplicate_locality_id=10498
    )
    # Durant, Oklahoma
    address_duplicate(
        true_location_id=6564, duplicate_location_id=14118, duplicate_locality_id=10920
    )
    # Miami, Oklahoma
    address_duplicate(
        true_location_id=5414, duplicate_location_id=15046, duplicate_locality_id=11848
    )

    op.execute("UPDATE localities SET name = replace(name, ',', '')")
    op.create_check_constraint(
        "localities_name_check",
        "localities",
        "name NOT LIKE '%,%'",
    )


def downgrade() -> None:
    op.drop_constraint("localities_name_check", "localities", type_="check")
