from sqlalchemy import delete

from db.models.implementations.core.data_source.core import DataSource
from db.queries.builder.core import QueryBuilderBase
from endpoints.v3.sync.shared.models.request.delete import SourceManagerDeleteRequest


class SourceManagerDeleteDataSourcesQueryBuilder(QueryBuilderBase):
    def __init__(self, request: SourceManagerDeleteRequest):
        super().__init__()
        self.request = request

    def run(self) -> None:
        statement = delete(DataSource).where(DataSource.id.in_(self.request.ids))

        self.execute(statement)
