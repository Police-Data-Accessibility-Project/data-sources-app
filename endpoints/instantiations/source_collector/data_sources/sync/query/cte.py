from typing import final

from sqlalchemy import select, func

from db.models.implementations import LinkAgencyDataSource


@final
class AgencyIdsCTE:
    def __init__(self):
        self.query = (
            select(
                func.array_agg(LinkAgencyDataSource.agency_id).label("agency_ids"),
                LinkAgencyDataSource.data_source_id,
            )
            .group_by(LinkAgencyDataSource.data_source_id)
            .cte(name="agency_ids")
        )

    @property
    def agency_ids(self) -> list[int]:
        return self.query.c.agency_ids

    @property
    def data_source_id(self) -> int:
        return self.query.c.data_source_id
