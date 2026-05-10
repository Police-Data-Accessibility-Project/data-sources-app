from typing import Any

from sqlalchemy import select

from db.dynamic_query_constructor import DynamicQueryConstructor
from endpoints.instantiations.data_sources_.get.convert import (
    data_source_to_get_data_sources_output,
)
from db.models.implementations.core.data_source.core import DataSource
from db.queries.builder.core import QueryBuilderBase


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
            select(DataSource)
            .options(*load_options)
            .where(DataSource.id == self.data_source_id)
        )

        result: DataSource = (
            self.session.execute(query).scalars(DataSource).first()
        )
        if result is None:
            return None

        data_source_dictionary = data_source_to_get_data_sources_output(
            result,
            data_requests_columns=self.data_requests_columns,
            data_sources_columns=self.data_sources_columns,
        )

        return data_source_dictionary
