from typing import Any, Sequence

from sqlalchemy import select, func, RowMapping
from sqlalchemy.orm import Session

from db.models.implementations import LinkAgencyDataSource, LinkAgencyLocation
from db.models.implementations.core.agency.core import Agency
from db.models.implementations.core.data_source.core import DataSource
from db.models.implementations.core.location.core import Location
from db.models.implementations.core.location.locality import Locality
from db.models.implementations.core.location.us_state import USState
from db.models.implementations.core.record.category import RecordCategory
from db.models.implementations.core.record.type import RecordType
from db.queries.builder.core import QueryBuilderBase
from endpoints.instantiations.search.core.models.response import SearchResponseDTO
from endpoints.instantiations.search.core.queries.locations import AssociatedLocationsCTEContainer
from middleware.enums import RecordTypes
from middleware.primary_resource_logic.search.helpers import format_search_results
from middleware.util.argument_checking import check_for_mutually_exclusive_arguments
from utilities.enums import RecordCategoryEnum

from db.helpers_ import session as sh

class SearchQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        location_id: int | None = None,
        record_categories: list[RecordCategoryEnum] | None = None,
        record_types: list[RecordTypes] | None = None,
    ):
        super().__init__()
        check_for_mutually_exclusive_arguments(
            arg1=record_categories,
            arg2=record_types)
        self.location_id = location_id
        self.record_categories = record_categories
        self.record_types = record_types

    def build(self, session: Session) -> SearchResponseDTO:

        query = (
            select(
                DataSource.id,
                DataSource.name.label("data_source_name"),
                DataSource.description,
                RecordType.name.label("record_type"),
                DataSource.source_url,
                DataSource.record_formats,
                DataSource.coverage_start,
                DataSource.coverage_end,
                DataSource.agency_supplied,
                Agency.name.label("agency_name"),
                func.string_agg(
                    Locality.name,
                    ", "
                ).label("municipality"),
                USState.state_iso,
                Agency.jurisdiction_type
            )
            .join(
                LinkAgencyDataSource,
                LinkAgencyDataSource.data_source_id == DataSource.id,
            )
            .join(
                Agency,
                LinkAgencyDataSource.agency_id == Agency.id,
            )
            .outerjoin(
                LinkAgencyLocation,
                LinkAgencyLocation.agency_id == Agency.id,
            )
            .join(
                Location,
                Location.id == LinkAgencyLocation.location_id,
            )
            .outerjoin(
                USState,
                USState.id == Location.state_id,
            )
            .outerjoin(
                Locality,
                Locality.id == Location.locality_id,
            )
            .join(
                RecordType,
                RecordType.id == DataSource.record_type_id,
            )
        )
        if self.location_id is not None:
            associated_locations_cte = AssociatedLocationsCTEContainer(self.location_id)
            query = query.join(
                associated_locations_cte.cte,
                associated_locations_cte.cte.c.id == Location.id,
            )
        if self.record_categories is not None:
            query = (
                query.join(
                    RecordCategory,
                    RecordCategory.id == RecordType.category_id,
                )
                .where(
                    RecordCategory.name.in_([rc.value for rc in self.record_categories])
                )
            )
        if self.record_types is not None:
            query = (
                query
                .where(
                    RecordType.name.in_([rt.value for rt in self.record_types])
                )
            )

        query = (
            query
            .where(
                DataSource.approval_status == 'approved',
                DataSource.url_status != 'broken'
            )
            .group_by(
                DataSource.id,
                DataSource.name,
                DataSource.description,
                RecordType.name,
                DataSource.source_url,
                DataSource.record_formats,
                DataSource.coverage_start,
                DataSource.coverage_end,
                DataSource.agency_supplied,
                Agency.name,
                USState.state_iso,
                Agency.jurisdiction_type
            )
        )

        results: Sequence[RowMapping] = sh.mappings(session, query=query)
        search_results_json: dict = format_search_results(results)
        return SearchResponseDTO(**search_results_json)