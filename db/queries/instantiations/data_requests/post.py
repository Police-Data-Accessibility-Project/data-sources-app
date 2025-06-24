from typing import override

from db.models.implementations import LinkLocationDataRequest
from db.models.implementations.core.data_request.core import DataRequest
from db.queries.builder import QueryBuilderBase
from middleware.schema_and_dto.dtos.data_requests.post import DataRequestsPostDTO


class DataRequestsPostQueryBuilder(QueryBuilderBase):

    def __init__(self, dto: DataRequestsPostDTO, user_id: int):
        super().__init__()
        self.dto = dto
        self.user_id = user_id

    def _add_data_request(self) -> int:
        request_info = self.dto.request_info
        data_request = DataRequest(
            title=request_info.title,
            submission_notes=request_info.submission_notes,
            creator_user_id=self.user_id,
            request_urgency=request_info.request_urgency.value,
            data_requirements=request_info.data_requirements,
        )
        self.session.add(data_request)
        self.session.flush()
        return data_request.id

    def _add_locations(self, dr_id: int):
        location_ids = (
            self.dto.location_ids if self.dto.location_ids is not None else []
        )
        for location_id in location_ids:
            self.session.add(
                LinkLocationDataRequest(data_request_id=dr_id, location_id=location_id)
            )

    @override
    def run(self) -> int:
        dr_id = self._add_data_request()
        self._add_locations(dr_id)
        return dr_id
