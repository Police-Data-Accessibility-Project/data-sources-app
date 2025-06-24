from typing import Any

from sqlalchemy import CTE, select, Subquery, func

from db.models.implementations.core.location.core import Location
from db.models.implementations.core.location.county import County
from db.models.implementations.core.location.locality import Locality
from db.models.implementations.core.location.us_state import USState
from db.models.implementations.core.recent_search.core import RecentSearch
from db.models.implementations.core.record.category import RecordCategory
from db.models.implementations.link import LinkRecentSearchRecordCategories
from db.queries.builder_.core import QueryBuilderBase


class GetUserRecentSearchesQueryBuilder(QueryBuilderBase):

    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id

        # Labels
        self.search_id_label = "search_id"
        self.record_categories_label = "record_categories"
        self.state_label = "state"
        self.county_label = "county"
        self.locality_label = "locality"
        self.location_id_label = "location_id"
        self.location_type_label = "location_type"

        # Queries
        self.base_cte = self.get_base_cte()
        self.record_category_subquery = self.get_record_category_subquery(self.base_cte)
        self.location_info_subquery = self.get_location_info_subquery(self.base_cte)

    def get_base_cte(self) -> CTE:
        return (
            select(RecentSearch.id.label(self.search_id_label))
            .where(RecentSearch.user_id == self.user_id)
            .order_by(RecentSearch.id.desc())
            .limit(10)
            .cte("recent_searches_cte")
        )

    def get_record_category_subquery(self, base_cte: CTE) -> Subquery:
        search_id = base_cte.c[self.search_id_label]

        return (
            select(
                search_id,
                func.array_agg(RecordCategory.name).label(self.record_categories_label),
            )
            .select_from(base_cte)
            .outerjoin(
                LinkRecentSearchRecordCategories,
                LinkRecentSearchRecordCategories.recent_search_id == search_id,
            )
            .outerjoin(
                RecordCategory,
                RecordCategory.id
                == LinkRecentSearchRecordCategories.record_category_id,
            )
            .group_by(search_id)
            .subquery("record_categories")
        )

    def get_location_info_subquery(self, base_cte: CTE) -> Subquery:
        search_id = base_cte.c[self.search_id_label]

        return (
            select(
                search_id,
                Location.id.label(self.location_id_label),
                Location.type.label(self.location_type_label),
                USState.state_name.label(self.state_label),
                County.name.label(self.county_label),
                Locality.name.label(self.locality_label),
            )
            .select_from(base_cte)
            .join(RecentSearch, RecentSearch.id == search_id)
            .outerjoin(Location, Location.id == RecentSearch.location_id)
            .outerjoin(USState, USState.id == Location.state_id)
            .outerjoin(County, County.id == Location.county_id)
            .outerjoin(Locality, Locality.id == Location.locality_id)
            .subquery("location_info")
        )

    def run(self) -> Any:
        search_id = self.base_cte.c[self.search_id_label]

        query = (
            select(
                search_id,
                self.location_info_subquery.c[self.location_id_label],
                self.location_info_subquery.c[self.location_type_label],
                self.location_info_subquery.c[self.state_label],
                self.location_info_subquery.c[self.county_label],
                self.location_info_subquery.c[self.locality_label],
                self.record_category_subquery.c[self.record_categories_label],
            )
            .select_from(self.base_cte)
            .join(
                self.location_info_subquery,
                self.location_info_subquery.c[self.search_id_label] == search_id,
            )
            .join(
                self.record_category_subquery,
                self.record_category_subquery.c[self.search_id_label] == search_id,
            )
        )

        raw_results = self.execute(query).mappings().all()
        results = []

        for result in raw_results:
            record_categories = result[self.record_categories_label]
            if record_categories[0] is None:
                record_categories = []

            results.append(
                {
                    "location_id": result[self.location_id_label],
                    "state_name": result[self.state_label],
                    "county_name": result[self.county_label],
                    "locality_name": result[self.locality_label],
                    "location_type": result[self.location_type_label],
                    "record_categories": record_categories,
                }
            )

        return {
            "data": results,
            "metadata": {
                "count": len(results),
            },
        }
