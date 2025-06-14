from typing import Optional, Any

from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from db.constants import PAGE_SIZE
from db.enums import LocationType
from db.models.implementations.core.location.core import Location
from db.queries.builder import QueryBuilderBase


class GetManyLocationsQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        page: int,
        has_coordinates: Optional[bool] = None,
        type_: Optional[LocationType] = None,
    ):
        super().__init__()
        self.page = page
        self.has_coordinates = has_coordinates
        self.type_ = type_

    def run(self) -> Any:
        # TODO: QueryBuilder
        query = select(Location)
        if self.has_coordinates is not None:
            if self.has_coordinates:
                query = query.where(
                    and_(
                        Location.lat != None,
                        Location.lng != None,
                    )
                )
            else:
                query = query.where(
                    and_(
                        Location.lat == None,
                        Location.lng == None,
                    )
                )
        if self.type_ is not None:
            query = query.where(Location.type == self.type_.value)

        # Select In Load
        for relationship in (
            "locality",
            "county",
            "state",
        ):
            query = query.options(selectinload(getattr(Location, relationship)))

        # Pagination
        query = query.offset(
            (self.page - 1) * PAGE_SIZE).limit(PAGE_SIZE)

        raw_results = self.session.execute(query).scalars().all()
        results = []
        for raw_result in raw_results:
            result = {
                "location_id": raw_result.id,
                "type": raw_result.type,
                "state_name": (
                    raw_result.state.state_name
                    if raw_result.state is not None
                    else None
                ),
                "state_iso": (
                    raw_result.state.state_iso if raw_result.state is not None else None
                ),
                "county_name": (
                    raw_result.county.name if raw_result.county is not None else None
                ),
                "locality_name": (
                    raw_result.locality.name
                    if raw_result.locality is not None
                    else None
                ),
                "county_fips": (
                    raw_result.county.fips if raw_result.county is not None else None
                ),
                "coordinates": {
                    "lat": raw_result.lat,
                    "lng": raw_result.lng,
                },
            }
            results.append(result)

        return results