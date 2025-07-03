from typing import Any, Optional, Sequence

from sqlalchemy import asc, select

from db.constants import PAGE_SIZE
from db.db_client_dataclasses import OrderByParameters
from db.dynamic_query_constructor import DynamicQueryConstructor
from db.enums import ApprovalStatus
from db.helpers import get_offset
from db.helpers_.result_formatting import data_source_to_get_data_sources_output
from db.models.implementations.core.data_source.core import DataSource
from db.models.implementations.core.data_source.expanded import DataSourceExpanded
from db.queries.builder.core import QueryBuilderBase
from middleware.enums import Relations


class GetDataSourcesQueryBuilder(QueryBuilderBase):
    def __init__(
        self,
        data_sources_columns: list[str],
        data_requests_columns: list[str],
        order_by: Optional[OrderByParameters] = None,
        page: Optional[int] = 1,
        limit: Optional[int] = PAGE_SIZE,
        approval_status: Optional[ApprovalStatus] = None,
    ):
        super().__init__()
        self.data_sources_columns = data_sources_columns
        self.data_requests_columns = data_requests_columns
        self.order_by = order_by
        self.page = page
        self.limit = limit
        self.approval_status = approval_status

    def run(self) -> Any:
        order_by_clause = DynamicQueryConstructor.get_sql_alchemy_order_by_clause(
            order_by=self.order_by,
            relation=Relations.DATA_SOURCES.value,
            default=asc(DataSourceExpanded.id),
        )

        load_options = DynamicQueryConstructor.data_sources_get_load_options(
            data_requests_columns=self.data_requests_columns,
            data_sources_columns=self.data_sources_columns,
        )

        # TODO: This format can be extracted to a function (see get_agencies)
        query = select(DataSourceExpanded)

        if self.approval_status is not None:
            query = query.where(
                DataSourceExpanded.approval_status == self.approval_status.value
            )

        query = (
            query.options(*load_options).order_by(order_by_clause).limit(self.limit)
        ).offset(get_offset(self.page))

        results: Sequence[DataSourceExpanded] = (
            self.session.execute(query).scalars(DataSource).all()
        )
        final_results = []
        for result in results:
            data_source_dictionary = data_source_to_get_data_sources_output(
                result,
                data_sources_columns=self.data_sources_columns,
                data_requests_columns=self.data_requests_columns,
            )
            final_results.append(data_source_dictionary)

        return final_results
