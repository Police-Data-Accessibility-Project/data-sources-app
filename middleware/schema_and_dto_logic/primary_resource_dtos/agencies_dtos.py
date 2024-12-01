from typing import Optional

from middleware.enums import JurisdictionType, AgencyType
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    LocationInfoDTO,
    GetByIDBaseDTO,
)
from pydantic import BaseModel


class AgencyInfoPutDTO(BaseModel):
    submitted_name: str = None
    jurisdiction_type: JurisdictionType = None
    agency_type: AgencyType = AgencyType.NONE
    multi_agency: bool = False
    no_web_presence: bool = False
    approved: bool = False
    homepage_url: str = None
    lat: float = None
    lng: float = None
    defunct_year: str = None
    zip_code: str = None
    rejection_reason: str = None
    last_approval_editor: str = None
    submitter_contact: str = None


class AgencyInfoPostDTO(BaseModel):
    submitted_name: str
    jurisdiction_type: JurisdictionType
    agency_type: AgencyType
    multi_agency: bool = False
    no_web_presence: bool = False
    approved: bool = False
    homepage_url: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    defunct_year: Optional[str] = None
    zip_code: Optional[str] = None
    rejection_reason: Optional[str] = None
    last_approval_editor: Optional[str] = None
    submitter_contact: Optional[str] = None


class AgenciesPostDTO(BaseModel):
    agency_info: AgencyInfoPostDTO
    location_info: Optional[LocationInfoDTO] = None


class AgenciesPutDTO(BaseModel):
    agency_info: AgencyInfoPutDTO
    location_info: Optional[LocationInfoDTO] = None


class RelatedAgencyByIDDTO(GetByIDBaseDTO):
    agency_id: int

    def get_where_mapping(self):
        return {
            "data_source_id": int(self.resource_id),
            "agency_id": int(self.agency_id),
        }
