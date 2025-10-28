from sqlalchemy import delete

from db.models.implementations.core.agency.meta_urls.sqlalchemy import AgencyMetaURL
from db.queries.builder.core import QueryBuilderBase
from endpoints.v3.sync.shared.models.request.delete import SourceManagerDeleteRequest


class SourceManagerDeleteMetaURLsQueryBuilder(QueryBuilderBase):
    def __init__(self, request: SourceManagerDeleteRequest):
        super().__init__()
        self.request = request

    def run(self) -> None:
        statement = delete(AgencyMetaURL).where(AgencyMetaURL.id.in_(self.request.ids))

        self.execute(statement)
