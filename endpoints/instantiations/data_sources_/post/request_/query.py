from typing import Sequence

import sqlalchemy.exc
from sqlalchemy import RowMapping, select
from werkzeug.exceptions import BadRequest, Conflict, InternalServerError

from db.models.implementations.links.agency__data_source import LinkAgencyDataSource
from db.models.implementations.core.data_source.core import DataSource
from db.models.implementations.core.record.type import RecordType
from db.queries.builder.core import QueryBuilderBase
from endpoints.instantiations.data_sources_.post.request_.model import (
    PostDataSourceOuterRequest,
)
from endpoints.v3.source_manager.sync.data_sources.add.helpers import _value_if_not_none
from middleware.enums import RecordTypesEnum


class PostDataSourceQuery(QueryBuilderBase):
    def __init__(self, request: PostDataSourceOuterRequest):
        super().__init__()
        self.request = request.entry_data
        self.linked_agency_ids = request.linked_agency_ids

    def run(self) -> int:
        record_type_id_mapping: dict[RecordTypesEnum, int] = (
            self.get_record_type_id_mapping()
        )
        ds_request = self.request

        try:
            ds_insert = DataSource(
                source_url=ds_request.source_url,
                name=ds_request.name,
                description=ds_request.description,
                record_type_id=record_type_id_mapping[ds_request.record_type_name]
                if ds_request.record_type_name
                else None,
                agency_supplied=ds_request.agency_supplied,
                supplying_entity=ds_request.supplying_entity,
                agency_originated=ds_request.agency_originated,
                agency_aggregation=_value_if_not_none(ds_request.agency_aggregation),
                coverage_start=ds_request.coverage_start,
                coverage_end=ds_request.coverage_end,
                detail_level=ds_request.detail_level,
                access_types=[at.value for at in ds_request.access_types]
                if ds_request.access_types
                else None,
                data_portal_type=ds_request.data_portal_type,
                record_formats=ds_request.record_formats,
                update_method=_value_if_not_none(ds_request.update_method),
                readme_url=ds_request.readme_url,
                originating_entity=ds_request.originating_entity,
                retention_schedule=_value_if_not_none(ds_request.retention_schedule),
                scraper_url=ds_request.scraper_url,
                agency_described_not_in_database=ds_request.agency_described_not_in_database,
                data_portal_type_other=ds_request.data_portal_type_other,
                access_notes=ds_request.access_notes,
            )
        except Exception as e:
            raise InternalServerError(f"Error creating data source: {e}")

        try:
            self.session.add(ds_insert)
            self.session.flush()

            for agency_id in self.linked_agency_ids:
                link_insert = LinkAgencyDataSource(
                    data_source_id=ds_insert.id, agency_id=agency_id
                )
                self.session.add(link_insert)
        except sqlalchemy.exc.IntegrityError as e:
            sqlstate = getattr(e.orig, "sqlstate", None)
            if sqlstate == "23514":
                raise BadRequest(
                    "Invalid URL: URLs with fragments (#) are not allowed. "
                    "Please remove the fragment from the URL."
                )
            if sqlstate == "23505":
                raise Conflict(
                    "Duplicate URL: This URL and record type combination already exists as a data source."
                )
            raise InternalServerError(f"Error creating data source: {e}")

        return ds_insert.id

    def get_record_type_id_mapping(self) -> dict[RecordTypesEnum, int]:
        query = select(
            RecordType.id,
            RecordType.name,
        )
        mappings: Sequence[RowMapping] = self.mappings(query)
        return {
            RecordTypesEnum(mapping[RecordType.name]): mapping[RecordType.id]
            for mapping in mappings
        }
