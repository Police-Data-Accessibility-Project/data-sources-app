from sqlalchemy import delete

from db.models.implementations.core.agency.meta_urls.sqlalchemy import MetaURL
from db.queries.builder.core import QueryBuilderBase
from endpoints.v3.source_manager.sync.shared.models.request.delete import (
    SourceManagerDeleteRequest,
)


class SourceManagerDeleteMetaURLsQueryBuilder(QueryBuilderBase):
    def __init__(self, request: SourceManagerDeleteRequest):
        super().__init__()
        self.request = request

    def run(self) -> None:
        statement = delete(MetaURL).where(MetaURL.id.in_(self.request.ids))

        self.execute(statement)
