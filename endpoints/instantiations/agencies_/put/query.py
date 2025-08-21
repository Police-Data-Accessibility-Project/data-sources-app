from enum import Enum
from typing import Any

from sqlalchemy import delete, update

from db.models.implementations.core.agency.core import Agency
from db.models.implementations.core.agency.meta_urls.sqlalchemy import AgencyMetaURL
from db.queries.builder.core import QueryBuilderBase
from endpoints.instantiations.agencies_.put.dto import AgencyInfoPutDTO


class UpdateAgencyQueryBuilder(QueryBuilderBase):
    def __init__(self, dto: AgencyInfoPutDTO, agency_id: int):
        super().__init__()
        self.agency_id = agency_id
        self.dto = dto

    def run(self) -> None:
        if self.dto.meta_urls is not None:
            self.update_meta_urls(self.dto.meta_urls)

        agency_info_dict: dict[str, Any] = self.dto.model_dump()
        del agency_info_dict["meta_urls"]
        for key, value in agency_info_dict.items():
            if value is None:
                del agency_info_dict[key]
            # If enum, convert to string
            if isinstance(value, Enum):
                agency_info_dict[key] = value.value
        stmt = (
            update(Agency).where(Agency.id == self.agency_id).values(**agency_info_dict)
        )
        self.session.execute(stmt)

    def update_meta_urls(self, meta_urls: list[str]) -> None:
        # Delete existing meta URLs
        stmt = delete(AgencyMetaURL).where(AgencyMetaURL.agency_id == self.agency_id)
        self.session.execute(stmt)

        # Add new meta URLs
        for meta_url in meta_urls:
            insert_obj = AgencyMetaURL(url=meta_url, agency_id=self.agency_id)
            self.session.add(insert_obj)
