from db.models.implementations import LinkAgencyLocation
from db.models.implementations.core.agency.core import Agency
from db.models.implementations.core.agency.meta_urls.sqlalchemy import AgencyMetaURL
from db.queries.builder.core import QueryBuilderBase
from endpoints.instantiations.agencies_.post.dto import AgenciesPostDTO


class CreateAgencyQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        dto: AgenciesPostDTO,
        user_id: int | None = None
    ):
        super().__init__()
        self.user_id = user_id
        self.dto = dto


    def run(self) -> int:
        agency_id = self._add_agency()

        self._link_to_locations(agency_id)

        return agency_id

    def _add_agency(self) -> int:
        agency_info = self.dto.agency_info
        agency = Agency(
            name=agency_info.name,
            agency_type=agency_info.agency_type.value,
            jurisdiction_type=agency_info.jurisdiction_type.value,
            multi_agency=agency_info.multi_agency,
            no_web_presence=agency_info.no_web_presence,
            approval_status=agency_info.approval_status.value,
            defunct_year=agency_info.defunct_year,
            rejection_reason=agency_info.rejection_reason,
            last_approval_editor=agency_info.last_approval_editor,
            submitter_contact=agency_info.submitter_contact,
            creator_user_id=self.user_id,
        )
        self.session.add(agency)
        # Flush to get agency id
        self.session.flush()
        return agency.id

    def _link_to_meta_urls(self, agency_id: int) -> None:
        if self.dto.agency_info.meta_urls is not None:
            for meta_url in self.dto.agency_info.meta_urls:
                insert_obj = AgencyMetaURL(
                    url=meta_url,
                    agency_id=agency_id
                )
                self.session.add(insert_obj)

    def _link_to_locations(self, agency_id: int) -> None:
        if self.dto.location_ids is not None:
            for location_id in self.dto.location_ids:
                lal = LinkAgencyLocation(
                    location_id=location_id,
                    agency_id=agency_id
                )
                self.session.add(lal)