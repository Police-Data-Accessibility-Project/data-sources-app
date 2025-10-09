from sqlalchemy import select

from db.models.implementations.core.location.core import Location
from db.models.implementations.core.location.dependent import DependentLocation


class AssociatedLocationsCTEContainer:
    def __init__(self, location_id: int):
        self.location_id = location_id
        self.cte = (
            select(Location.id)
            .where(Location.id == location_id)
            .union(
                select(DependentLocation.dependent_location_id)
                .where(DependentLocation.parent_location_id == location_id)
                .union(
                    select(DependentLocation.parent_location_id).where(
                        DependentLocation.dependent_location_id == location_id
                    )
                )
            )
            .cte("associated_locations")
        )
