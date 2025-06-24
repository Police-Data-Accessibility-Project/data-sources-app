from typing import Any

from sqlalchemy import select

from db.dynamic_query_constructor import DynamicQueryConstructor
from db.helpers_.result_formatting import data_source_to_get_data_sources_output
from db.models.implementations.core.data_source.expanded import DataSourceExpanded
from db.queries.builder_.core import QueryBuilderBase


class GetDataSourceByIDQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        data_source_id: int,
        data_sources_columns: list[str],
        data_requests_columns: list[str],
    ):
        super().__init__()
        self.data_source_id = data_source_id
        self.data_sources_columns = data_sources_columns
        self.data_requests_columns = data_requests_columns

    def run(self) -> Any:
        load_options = DynamicQueryConstructor.data_sources_get_load_options(
            data_sources_columns=self.data_sources_columns,
            data_requests_columns=self.data_requests_columns,
        )

        query = (
            select(DataSourceExpanded)
            .options(*load_options)
            .where(DataSourceExpanded.id == self.data_source_id)
        )

        result: DataSourceExpanded = (
            self.session.execute(query).scalars(DataSourceExpanded).first()
        )
        if result is None:
            return None

        data_source_dictionary = data_source_to_get_data_sources_output(
            result,
            data_requests_columns=self.data_requests_columns,
            data_sources_columns=self.data_sources_columns,
        )

        return data_source_dictionary
