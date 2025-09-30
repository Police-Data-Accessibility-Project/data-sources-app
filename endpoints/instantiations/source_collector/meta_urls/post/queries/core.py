from typing import Any

import sqlalchemy

from db.models.implementations.core.agency.meta_urls.sqlalchemy import AgencyMetaURL
from db.queries.builder.core import QueryBuilderBase
from endpoints.instantiations.source_collector.meta_urls.post.dtos.request import \
    SourceCollectorMetaURLPostRequestInnerDTO
from endpoints.instantiations.source_collector.meta_urls.post.dtos.response import \
    SourceCollectorMetaURLPostResponseDTO, SourceCollectorMetaURLPostResponseInnerDTO
from endpoints.instantiations.source_collector.meta_urls.post.enums import MetaURLCreationResponse


class AddMetaURLsFromSourceCollectorQueryBuilder(QueryBuilderBase):

    def __init__(self, meta_urls: list[SourceCollectorMetaURLPostRequestInnerDTO]):
        super().__init__()
        self._meta_urls = meta_urls

    def run(self) -> SourceCollectorMetaURLPostResponseDTO:
        results: list[SourceCollectorMetaURLPostResponseInnerDTO] = []

        for meta_url in self._meta_urls:
            self.session.begin_nested()
            try:
                meta_url_db = AgencyMetaURL(
                    agency_id=meta_url.agency_id,
                    url=meta_url.url,
                )
                self.session.add(meta_url_db)
                self.session.flush()

                dto = SourceCollectorMetaURLPostResponseInnerDTO(
                    url=meta_url.url,
                    status=MetaURLCreationResponse.SUCCESS,
                    meta_url_id=meta_url_db.id,
                )
                results.append(dto)
            except sqlalchemy.exc.IntegrityError as e:
                self.session.rollback()
                dto = SourceCollectorMetaURLPostResponseInnerDTO(
                    url=meta_url.url,
                    status=MetaURLCreationResponse.FAILURE,
                    meta_url_id=None,
                    error=str(e),
                )
                results.append(dto)
            else:
                self.session.commit()

        return SourceCollectorMetaURLPostResponseDTO(
            meta_urls=results,
        )