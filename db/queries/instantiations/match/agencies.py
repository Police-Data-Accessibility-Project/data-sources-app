from typing import Optional, Any, List

from sqlalchemy import Select, func
from sqlalchemy.orm import load_only, selectinload

from db.enums import LocationType
from db.models.implementations.core.agency.core import Agency
from db.models.implementations.core.location.expanded import LocationExpanded
from db.queries.builder import QueryBuilderBase
from middleware.enums import AgencyType
from middleware.schema_and_dto.dtos.match.response import (
    AgencyMatchResponseLocationDTO,
    AgencyMatchResponseInnerDTO,
)


class GetSimilarAgenciesQueryBuilder(QueryBuilderBase):

    def __init__(self, name: str, location_id: Optional[int] = None):
        super().__init__()
        self.name = name
        self.location_id = location_id

    def run(self) -> List[AgencyMatchResponseInnerDTO]:
        """
        Retrieve agencies similar to the query
        Optionally filtering based on the location id
        """
        # TODO: QueryBuilder
        query = Select(
            Agency,
            func.similarity(Agency.name, self.name),
        ).options(
            load_only(Agency.id, Agency.name, Agency.agency_type),
            selectinload(Agency.locations).load_only(
                LocationExpanded.state_name,
                LocationExpanded.county_name,
                LocationExpanded.locality_name,
                LocationExpanded.type,
            ),
        )
        if self.location_id is not None:
            query = query.where(
                Agency.locations.any(LocationExpanded.id == self.location_id)
            )
        query = query.order_by(func.similarity(Agency.name, self.name).desc()).limit(10)
        execute_results = self.session.execute(query).all()
        if len(execute_results) == 0:
            return []

        def result_to_dto(agency: Agency, similarity: float):
            locations = []
            for location in agency.locations:
                location_dto = AgencyMatchResponseLocationDTO(
                    state=location.state_name,
                    county=location.county_name,
                    locality=location.locality_name,
                    location_type=LocationType(location.type),
                )
                locations.append(location_dto)

            return AgencyMatchResponseInnerDTO(
                id=agency.id,
                name=agency.name,
                agency_type=AgencyType(agency.agency_type),
                similarity=similarity,
                locations=locations,
            )

        dto_results = []
        for result, similarity in execute_results:
            if similarity == 1:
                return [
                    result_to_dto(result, similarity),
                ]
            dto = result_to_dto(result, similarity)
            dto_results.append(dto)

        return dto_results
