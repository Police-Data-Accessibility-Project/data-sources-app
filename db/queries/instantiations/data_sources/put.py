from typing import final, override

from sqlalchemy import update

from db.enums import ApprovalStatus
from db.models.implementations.core.data_source.core import DataSource
from db.queries.builder.core import QueryBuilderBase
from db.queries.builder.mixins.pending_event.data_source import (
    DataSourcePendingEventMixin,
)
from db.queries.builder.mixins.record_type import RecordTypeMixin
from middleware.enums import PermissionsEnum
from middleware.schema_and_dto.dtos.entry_create_update_request import EntryCreateUpdateRequestDTO
from middleware.util.type_conversion import dict_enums_to_values


@final
class DataSourcesPutQueryBuilder(
    QueryBuilderBase, RecordTypeMixin, DataSourcePendingEventMixin
):
    def __init__(
        self,
        data_source_id: int,
        dto: EntryCreateUpdateRequestDTO,
        permissions: list[PermissionsEnum],
        user_id: int,
    ):
        super().__init__()
        self.data_source_id = data_source_id
        self.dto = dto
        self.permissions = permissions
        self.user_id = user_id

    @override
    def run(self) -> None:
        self._update_data_source()

    def _update_data_source(self) -> None:
        d = {}
        entry = self.dto.entry_data
        for key, value in entry.items():
            if value is not None:
                d[key] = value
        self._handle_record_type_name(d)
        self._handle_approval_status(d)

        d = dict_enums_to_values(d)

        query = (
            update(DataSource).where(DataSource.id == self.data_source_id).values(**d)
        )
        _ = self.session.execute(query)

    def _handle_approval_status(self, d: dict) -> None:
        if "approval_status" in d:
            d["last_approval_editor"] = self.user_id
            approval_status = d["approval_status"]
            if approval_status == ApprovalStatus.APPROVED.value:
                self._add_pending_event_notification(self.data_source_id)

    def _handle_record_type_name(self, d: dict) -> None:
        if "record_type_name" in d:
            record_type_id = self._get_record_type_id(d["record_type_name"])
            d["record_type_id"] = record_type_id
            del d["record_type_name"]
