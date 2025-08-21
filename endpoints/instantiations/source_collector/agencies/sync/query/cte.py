from sqlalchemy import func, select, ColumnElement, CTE, ARRAY, cast, String

from db.models.implementations.core.agency.core import Agency
from db.models.implementations.core.agency.meta_urls.sqlalchemy import AgencyMetaURL


class AgencyMetaURLsCTE:

    def __init__(self):
        self._cte = (
            select(
                Agency.id,
                func.coalesce(
                    func.array_agg(
                        AgencyMetaURL.url
                    ).filter(AgencyMetaURL.url.isnot(None)),
                    cast({}, ARRAY(String))
                ).label("meta_urls"),
            )
            .outerjoin(AgencyMetaURL, Agency.id == AgencyMetaURL.agency_id)
            .group_by(Agency.id)
            .cte(name="agency_meta_urls")
        )

    @property
    def cte(self) -> CTE:
        return self._cte

    @property
    def agency_id(self) -> ColumnElement[int]:
        return self._cte.c.id

    @property
    def meta_urls(self) -> ColumnElement[list[str]]:
        return self._cte.c.meta_urls

