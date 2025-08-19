from sqlalchemy import select

from db.dynamic_query_constructor import DynamicQueryConstructor
from endpoints.instantiations.agencies_.get._shared.convert import agency_to_get_agencies_output
from db.models.implementations.core.agency.core import Agency
from db.queries.builder.core import QueryBuilderBase
from endpoints.instantiations.agencies_.get._shared.dto.base import AgenciesGetDTO


class GetAgencyByIDQueryBuilder(QueryBuilderBase):
    def __init__(self, agency_id: int):
        super().__init__()
        self.agency_id = agency_id

    def run(self) -> AgenciesGetDTO:
        load_options = DynamicQueryConstructor.agencies_get_load_options()

        query = select(Agency).options(*load_options).where(Agency.id == self.agency_id)

        result: Agency = self.session.execute(query).scalars(Agency).first()
        agency_dictionary = agency_to_get_agencies_output(
            result,
        )

        return agency_dictionary
