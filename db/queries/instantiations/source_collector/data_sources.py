import sqlalchemy

from db.enums import ApprovalStatus
from db.models.implementations import LinkAgencyDataSource
from db.models.implementations.core.data_source.core import DataSource
from db.models.implementations.core.record.type import RecordType
from db.queries.builder.core import QueryBuilderBase
from endpoints.instantiations.source_collector.data_sources.post.dtos.response import (
    SourceCollectorPostResponseInnerDTO,
)

from middleware.enums import DataSourceCreationResponse
from endpoints.instantiations.source_collector.data_sources.post.dtos.request import (
    SourceCollectorPostRequestInnerDTO,
)


class AddDataSourcesFromSourceCollectorQueryBuilder(QueryBuilderBase):

    def __init__(self, data_sources: list[SourceCollectorPostRequestInnerDTO]):
        super().__init__()
        self.data_sources = data_sources

    def get_record_type_cache(self) -> dict[str, int]:
        d = {}
        for record_type in self.session.query(RecordType).all():
            d[record_type.name] = record_type.id
        return d

    def run(self) -> list[SourceCollectorPostResponseInnerDTO]:
        record_type_cache = self.get_record_type_cache()
        results: list[SourceCollectorPostResponseInnerDTO] = []

        for data_source in self.data_sources:
            self.session.begin_nested()  # Starts a savepoint
            try:
                data_source_db = DataSource(
                    name=data_source.name,
                    description=data_source.description,
                    approval_status=ApprovalStatus.APPROVED.value,
                    source_url=data_source.source_url,
                    record_type_id=record_type_cache[data_source.record_type.value],
                    record_formats=data_source.record_formats,
                    data_portal_type=data_source.data_portal_type,
                    last_approval_editor=data_source.last_approval_editor,
                    supplying_entity=data_source.supplying_entity,
                    submission_notes="Auto-submitted from Source Collector",
                )
                self.session.add(data_source_db)
                self.session.flush()  # Execute the insert immediately
                for agency_id in data_source.agency_ids:
                    link = LinkAgencyDataSource(
                        data_source_id=data_source_db.id, agency_id=agency_id
                    )
                    self.session.add(link)

                self.session.flush()  # Execute the insert immediately

                # Success! Add to results
                dto = SourceCollectorPostResponseInnerDTO(
                    url=data_source.source_url,
                    status=DataSourceCreationResponse.SUCCESS,
                    data_source_id=data_source_db.id,
                )
                results.append(dto)

            except sqlalchemy.exc.IntegrityError as e:
                self.session.rollback()  # Roll back to the savepoint
                # Failure! Add to results
                dto = SourceCollectorPostResponseInnerDTO(
                    url=data_source.source_url,
                    status=DataSourceCreationResponse.FAILURE,
                    data_source_id=None,
                    error=str(e),
                )
                results.append(dto)
            else:
                self.session.commit()  # Release the savepoint

        return results
