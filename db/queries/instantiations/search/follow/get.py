from typing import Any

from sqlalchemy import select, Select
from sqlalchemy.orm import selectinload

from db.enums import LocationType
from db.helpers_.result_formatting import get_display_name
from db.models.implementations.core.location.core import Location
from db.models.implementations.core.record.type import RecordType
from db.models.implementations.links.user__followed_location import LinkUserFollowedLocation
from db.queries.builder.core import QueryBuilderBase


class GetUserFollowedSearchesQueryBuilder(QueryBuilderBase):
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id

    def location_selectin_loads(self):
        sil = selectinload(LinkUserFollowedLocation.location)
        return [
            sil.selectinload(Location.state),
            sil.selectinload(Location.county),
            sil.selectinload(Location.locality),
        ]

    def process_record_types(
        self, record_types: list[RecordType]
    ) -> dict[str, list[str]]:
        d = {}
        for rt in record_types:
            rc = rt.record_category.name
            if rc in d:
                d[rc].append(rt.name)
            else:
                d[rc] = [rt.name]
        return d

    def run(self) -> dict[str, Any]:
        query = self.build_query()

        raw_results: list[LinkUserFollowedLocation] = (
            self.execute(query).scalars().all()
        )
        return self.process_results(raw_results)

    def process_results(
        self, raw_results: list[LinkUserFollowedLocation]
    ) -> dict[str, Any]:
        final_results = []
        for result in raw_results:
            location = result.location
            location_type = LocationType(location.type)
            location_id = location.id
            state_name = (
                location.state.state_name if location.state is not None else None
            )
            county_name = location.county.name if location.county is not None else None
            locality_name = (
                location.locality.name if location.locality is not None else None
            )
            record_types = [rt for rt in result.record_types]
            final_results.append(
                {
                    "location_id": location_id,
                    "display_name": get_display_name(
                        location_type=location_type,
                        state_name=state_name,
                        county_name=county_name,
                        locality_name=locality_name,
                    ),
                    "state_name": state_name,
                    "county_name": county_name,
                    "locality_name": locality_name,
                    "subscriptions_by_category": self.process_record_types(
                        record_types
                    ),
                }
            )
        return {
            "metadata": {
                "count": len(final_results),
            },
            "data": final_results,
        }

    def build_query(self) -> Select:
        query = (
            select(LinkUserFollowedLocation)
            .where(LinkUserFollowedLocation.user_id == self.user_id)
            .options(
                *self.location_selectin_loads(),
                selectinload(LinkUserFollowedLocation.record_types).selectinload(
                    RecordType.record_category
                ),
            )
        )
        return query
