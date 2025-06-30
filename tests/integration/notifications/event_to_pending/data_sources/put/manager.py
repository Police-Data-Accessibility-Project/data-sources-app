from db.client.core import DatabaseClient
from db.enums import ApprovalStatus
from middleware.enums import PermissionsEnum
from middleware.schema_and_dto.schemas.data_sources.base import (
    EntryCreateUpdateRequestDTO,
)
from tests.integration.notifications.event_to_pending.data_sources.manager import (
    EventToPendingDataSourcesTestManager,
)


class EventToPendingDataSourcesPutTestManager:
    def __init__(self, tdc):
        self.inner_manager = EventToPendingDataSourcesTestManager(tdc)
        self.user_id = tdc.user().id
        self.db_client: DatabaseClient = tdc.db_client
        self.data_source_id = tdc.data_source(approval_status=ApprovalStatus.PENDING).id
        assert not self._is_in_pending()

    def update_approval_status(self, approval_status: ApprovalStatus):
        self.db_client.update_data_source_v2(
            dto=EntryCreateUpdateRequestDTO(
                entry_data={"approval_status": approval_status.value}
            ),
            data_source_id=self.data_source_id,
            permissions=[PermissionsEnum.DB_WRITE],
            user_id=self.user_id,
        )

    def _is_in_pending(self) -> bool:
        return self.inner_manager.is_in_pending(self.data_source_id)
