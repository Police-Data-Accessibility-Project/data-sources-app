from sqlalchemy import select

from db.models.implementations.core.data_request.core import DataRequest
from db.queries.builder.core import QueryBuilderBase


class DataRequestExistsQueryBuilder(QueryBuilderBase):
    def __init__(self, data_request_id: int):
        super().__init__()
        self.data_request_id = data_request_id

    def run(self) -> bool:
        query = select(DataRequest.id).where(DataRequest.id == self.data_request_id)

        return self.results_exists(query)
