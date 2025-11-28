from db.models.implementations import LinkDataSourceDataRequest
from db.queries.builder.core import QueryBuilderBase


class DataRequestRelatedSourceAddLinkQueryBuilder(QueryBuilderBase):
    def __init__(
        self,
        data_request_id: int,
        data_source_id: int,
    ):
        super().__init__()
        self.data_request_id = data_request_id
        self.data_source_id = data_source_id

    def run(self) -> None:
        link = LinkDataSourceDataRequest(
            request_id=self.data_request_id,
            data_source_id=self.data_source_id,
        )
        self.add(link)
