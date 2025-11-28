from sqlalchemy import select

from db.models.implementations.core.data_source.core import DataSource
from db.queries.builder.core import QueryBuilderBase


class DataSourceExistsQueryBuilder(QueryBuilderBase):
    def __init__(self, data_source_id: int):
        super().__init__()
        self.data_source_id = data_source_id

    def run(self) -> bool:
        query = (
            select(DataSource.id)
            .where(DataSource.id == self.data_source_id)
        )

        return self.results_exists(query)