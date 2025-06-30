from typing import final, override

from sqlalchemy import update, select
from werkzeug.exceptions import Forbidden

from db.enums import RelationRoleEnum, ColumnPermissionEnum, RequestStatus, EventType
from db.models.implementations.core.data_request.core import DataRequest
from db.models.implementations.core.data_request.github_issue_info import (
    DataRequestsGithubIssueInfo,
)
from db.queries.builder.core import QueryBuilderBase
from db.queries.builder.mixins.pending_event.data_request import (
    DataRequestPendingEventMixin,
)
from middleware.column_permission.core import get_permitted_columns
from middleware.enums import PermissionsEnum, Relations
from middleware.schema_and_dto.dtos.data_requests.put import (
    DataRequestsPutOuterDTO,
    DataRequestsPutDTO,
)


@final
class DataRequestsPutQueryBuilder(QueryBuilderBase, DataRequestPendingEventMixin):
    def __init__(
        self,
        dto: DataRequestsPutOuterDTO,
        data_request_id: int,
        user_id: int | None = None,
        permissions: list[PermissionsEnum] | None = None,
        bypass_permissions: bool = False,
    ):
        super().__init__()
        self.dto = dto
        self.data_request_id = data_request_id
        self.user_id = user_id
        self.permissions = permissions
        self.bypass_permissions = bypass_permissions

    def __post_init__(self) -> None:
        if self.bypass_permissions:
            if self.user_id is not None:
                raise ValueError("If bypass_permissions is True, user_id must be None")
            if self.permissions is not None:
                raise ValueError(
                    "If bypass_permissions is True, permissions must be None"
                )
        else:
            if self.user_id is None:
                raise ValueError("user_id is required")
            if self.permissions is None:
                raise ValueError("permissions is required")

    @override
    def run(self) -> None:
        self._check_permissions()
        self._update_data_request()
        if self.dto.entry_data.github_issue_url is not None:
            self._add_github_issue()
        self._handle_potential_event_notification()

    def _handle_potential_event_notification(self):
        if self.dto.entry_data.request_status == RequestStatus.READY_TO_START:
            self._add_pending_event_notification(
                self.data_request_id, event_type=EventType.REQUEST_READY_TO_START
            )
        if self.dto.entry_data.request_status == RequestStatus.COMPLETE:
            self._add_pending_event_notification(
                self.data_request_id, event_type=EventType.REQUEST_COMPLETE
            )

    def _add_github_issue(self) -> None:
        url = self.dto.entry_data.github_issue_url
        number = self.dto.entry_data.github_issue_number

        obj = DataRequestsGithubIssueInfo(
            data_request_id=self.data_request_id,
            github_issue_url=url,
            github_issue_number=int(number),
        )
        self.session.add(obj)

    def _update_data_request(self) -> None:
        d = {}
        entry: DataRequestsPutDTO = self.dto.entry_data
        if entry.title is not None:
            d["title"] = entry.title
        if entry.submission_notes is not None:
            d["submission_notes"] = entry.submission_notes
        if entry.request_urgency is not None:
            d["request_urgency"] = entry.request_urgency.value
        if entry.coverage_range is not None:
            d["coverage_range"] = entry.coverage_range
        if entry.data_requirements is not None:
            d["data_requirements"] = entry.data_requirements
        if entry.request_status is not None:
            d["request_status"] = entry.request_status.value
        if entry.archive_reason is not None:
            d["archive_reason"] = entry.archive_reason
        if entry.internal_notes is not None:
            d["internal_notes"] = entry.internal_notes
        if entry.record_types_required is not None:
            d["record_types_required"] = [
                rt.value for rt in entry.record_types_required
            ]
        if entry.pdap_response is not None:
            d["pdap_response"] = entry.pdap_response

        query = (
            update(DataRequest)
            .where(DataRequest.id == self.data_request_id)
            .values(**d)
        )

        _ = self.session.execute(query)

    def _check_permissions(self) -> None:
        if self.bypass_permissions:
            return
        relation_role = self._get_relation_role()
        permitted_columns = get_permitted_columns(
            relation=Relations.DATA_REQUESTS.value,
            role=relation_role,
            user_permission=ColumnPermissionEnum.WRITE,
        )
        modified_columns = self._get_modified_columns()
        if len(set(modified_columns) - set(permitted_columns)) > 0:
            forbidden_columns = set(modified_columns) - set(permitted_columns)
            raise Forbidden(
                f"You do not have permission to edit the following columns: {forbidden_columns}"
            )

    def _get_modified_columns(self) -> list[str]:
        columns = []
        for (
            key,
            value,
        ) in self.dto.entry_data.__dict__.items():  # pyright: ignore [reportAny]
            if value is not None:
                columns.append(key)  # pyright: ignore [reportUnknownMemberType]
        return columns  # pyright: ignore [reportUnknownVariableType]

    def _user_is_creator(self) -> bool:
        query = select(DataRequest.id).where(
            DataRequest.creator_user_id == self.user_id,
            DataRequest.id == self.data_request_id,
        )
        data_request_id = self.session.scalar(query)
        return data_request_id is not None

    def _get_relation_role(self) -> RelationRoleEnum:
        if PermissionsEnum.DB_WRITE in self.permissions:
            return RelationRoleEnum.ADMIN
        if self._user_is_creator():
            return RelationRoleEnum.OWNER
        return RelationRoleEnum.STANDARD
