from typing import final

from sqlalchemy import CTE, union_all, select

from db.models.implementations.core.location.core import Location
from db.models.implementations.core.location.dependent import DependentLocation


def get_dependent_location_cte() -> CTE:
    """
    CTE for dependent locations
    Used to find all locations that are dependent on a given location
    (including the location itself)
    """
    return union_all(
        select(
            Location.id.label("location_id"),
            DependentLocation.dependent_location_id,
        ).join(
            DependentLocation,
            Location.id == DependentLocation.parent_location_id,
            isouter=True,
        ),
        select(
            Location.id.label("location_id"),
            Location.id.label("dependent_location_id"),
        ),
    ).cte(name="dependent_locations_cte")


@final
class DependentLocationCTE:
    def __init__(self):
        self._query = union_all(
            select(
                Location.id.label("location_id"),
                DependentLocation.dependent_location_id,
            ).join(
                DependentLocation,
                Location.id == DependentLocation.parent_location_id,
                isouter=True,
            ),
            select(
                Location.id.label("location_id"),
                Location.id.label("dependent_location_id"),
            ),
        ).cte(name="dependent_locations_cte")

    @property
    def query(self):
        return self._query

    @property
    def location_id(self):
        return self._query.c.location_id

    @property
    def dependent_location_id(self):
        return self._query.c.dependent_location_id
