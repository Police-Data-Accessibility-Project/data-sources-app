from typing import override, final


from db.enums import ApprovalStatus
from db.helpers import enum_value_or_none
from db.models.implementations import LinkAgencyDataSource
from db.models.implementations.core.data_source.core import DataSource
from db.queries.builder.core import QueryBuilderBase
from db.queries.builder.mixins.pending_event.data_source import (
    DataSourcePendingEventMixin,
)
from db.queries.builder.mixins.record_type import RecordTypeMixin
from middleware.schema_and_dto.dtos.data_sources.post import (
    DataSourcesPostDTO,
    DataSourceEntryDataPostDTO,
)
from middleware.util.type_conversion import enum_list_to_values


@final
class DataSourcesPostSingleQueryBuilder(
    QueryBuilderBase, RecordTypeMixin, DataSourcePendingEventMixin
):
    def __init__(self, dto: DataSourcesPostDTO):
        super().__init__()
        self.dto = dto

    @override
    def run(self) -> int:
        entry = self.dto.entry_data
        data_source_id = self._add_data_source(entry)
        linked_agency_ids = self.dto.linked_agency_ids
        if linked_agency_ids is not None:
            self._link_to_agencies(data_source_id, linked_agency_ids)
        if self.dto.entry_data.approval_status == ApprovalStatus.APPROVED:
            self._add_pending_event_notification(data_source_id)
        return data_source_id

    def _link_to_agencies(self, data_source_id: int, agency_ids: list[int]):
        for agency_id in agency_ids:
            link = LinkAgencyDataSource(
                data_source_id=data_source_id, agency_id=agency_id
            )
            self.session.add(link)

    def _add_data_source(self, entry: DataSourceEntryDataPostDTO) -> int:
        data_source = DataSource(
            name=entry.name,
            description=entry.description,
            approval_status=entry.approval_status.value,
            source_url=entry.source_url,
            agency_supplied=entry.agency_supplied,
            supplying_entity=entry.supplying_entity,
            agency_originated=entry.agency_originated,
            agency_aggregation=enum_value_or_none(entry.agency_aggregation),
            coverage_start=entry.coverage_start,
            coverage_end=entry.coverage_end,
            detail_level=enum_value_or_none(entry.detail_level),
            access_types=enum_list_to_values(entry.access_types),
            data_portal_type=entry.data_portal_type,
            record_formats=entry.record_formats,
            update_method=enum_value_or_none(entry.update_method),
            tags=entry.tags,
            readme_url=entry.readme_url,
            originating_entity=entry.originating_entity,
            retention_schedule=enum_value_or_none(entry.retention_schedule),
            scraper_url=entry.scraper_url,
            submitter_contact_info=entry.submitter_contact_info,
            submission_notes=entry.submission_notes,
            agency_described_not_in_database=entry.agency_described_not_in_database,
            data_portal_type_other=entry.data_portal_type_other,
            access_notes=entry.access_notes,
            url_status=enum_value_or_none(entry.url_status),
            data_source_request=entry.data_source_request,
            rejection_note=entry.rejection_note,
            last_approval_editor=entry.last_approval_editor,
            broken_source_url_as_of=entry.broken_source_url_as_of,
            record_type_id=self._get_record_type_id(entry.record_type_name.value),
        )
        self.session.add(data_source)

        self.session.flush()
        return data_source.id
