from sqlalchemy import select

from db.enums import RequestStatus
from db.models.implementations.core.notification.pending.data_request import (
    DataRequestPendingEventNotification,
)
from middleware.schema_and_dto.dtos.data_requests.put import (
    DataRequestsPutOuterDTO,
    DataRequestsPutDTO,
)
from tests.helper_scripts.helper_classes.test_data_creator.db_client_.core import (
    TestDataCreatorDBClient,
)


class EventToPendingDataRequestsTestManager:

    def __init__(self, tdc: TestDataCreatorDBClient):
        self.tdc = tdc
        self.db_client = tdc.db_client
        data_request = tdc.data_request(request_status=RequestStatus.INTAKE)
        self.data_request_id = data_request.id
        # Should not yet be in queue
        assert not self.is_in_pending()

    def is_in_pending(self) -> bool:
        query = select(DataRequestPendingEventNotification.id).where(
            DataRequestPendingEventNotification.data_request_id == self.data_request_id
        )
        id_ = self.db_client.scalar(query)
        return id_ is not None

    def update_request_status(self, request_status: RequestStatus) -> None:
        self.db_client.update_data_request_v2(
            data_request_id=self.data_request_id,
            dto=DataRequestsPutOuterDTO(
                entry_data=DataRequestsPutDTO(request_status=request_status)
            ),
            bypass_permissions=True,
        )
