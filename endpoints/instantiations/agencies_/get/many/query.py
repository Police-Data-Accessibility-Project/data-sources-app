from typing import Any, Sequence

from sqlalchemy import asc, select

from db.dynamic_query_constructor import DynamicQueryConstructor
from db.helpers import get_offset
from endpoints.instantiations.agencies_.get._shared.convert import (
    agency_to_get_agencies_output,
)
from db.models.implementations.core.agency.core import Agency
from db.queries.builder.core import QueryBuilderBase
from db.queries.models.get_params import GetParams
from middleware.enums import Relations


class GetAgenciesQueryBuilder(QueryBuilderBase):
    def __init__(
        self,
        params: GetParams,
    ):
        super().__init__()
        self.params = params

    def run(self) -> Any:
        order_by_clause = DynamicQueryConstructor.get_sql_alchemy_order_by_clause(
            order_by=self.params.order_by,
            relation=Relations.AGENCIES.value,
            default=asc(Agency.id),
        )

        load_options = DynamicQueryConstructor.agencies_get_load_options(
            requested_columns=self.params.requested_columns
        )

        # TODO: This format can be extracted to a function (see get_data_sources)
        query = select(Agency)

        query = (
            query.options(*load_options)
            .order_by(order_by_clause)
            .limit(self.params.limit)
            .offset(get_offset(self.params.page))
        )

        results: Sequence[Agency] = self.session.execute(query).scalars(Agency).all()
        final_results = []
        for result in results:
            agency_dictionary = agency_to_get_agencies_output(
                result, requested_columns=self.params.requested_columns
            )
            final_results.append(agency_dictionary)

        return final_results
