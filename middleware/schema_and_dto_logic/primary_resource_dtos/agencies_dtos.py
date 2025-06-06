from typing import Optional

from db.enums import ApprovalStatus
from middleware.enums import JurisdictionType, AgencyType
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    LocationInfoDTO,
    GetByIDBaseDTO,
    GetManyBaseDTO,
)
from pydantic import BaseModel, Field


class AgencyInfoBaseDTO(BaseModel):
    multi_agency: bool = Field(
        default=False,
        description="Whether or not the agency is a multi-agency.",
    )
    no_web_presence: bool = Field(
        default=False,
        description="Whether or not the agency has no web presence.",
    )
    approval_status: ApprovalStatus = Field(
        default=ApprovalStatus.PENDING,
        description="The approval status of the agency.",
    )
    homepage_url: Optional[str] = Field(
        default=None,
        description="The homepage URL of the agency.",
    )
    lat: Optional[float] = Field(
        default=None,
        description="Latitude of the location of the agency",
    )
    lng: Optional[float] = Field(
        default=None,
        description="Longitude of the location of the agency",
    )
    defunct_year: Optional[str] = Field(
        default=None,
        description="If present, denotes an agency which has defunct but may still have relevant records.",
    )
    rejection_reason: Optional[str] = Field(
        default=None,
        description="If present, denotes a rejection reason for an agency.",
    )
    last_approval_editor: Optional[str] = Field(
        default=None,
        description="The user who last approved the agency.",
    )
    submitter_contact: Optional[str] = Field(
        default=None,
        description="The contact information of the user who submitted the agency.",
    )


class AgencyInfoPutDTO(AgencyInfoBaseDTO):
    name: str = None
    jurisdiction_type: JurisdictionType = None
    agency_type: AgencyType = None


class AgencyInfoPostDTO(AgencyInfoBaseDTO):
    name: str
    jurisdiction_type: JurisdictionType
    agency_type: AgencyType


class AgenciesPostDTO(BaseModel):
    agency_info: AgencyInfoPostDTO
    location_ids: Optional[list[int]] = None


class RelatedAgencyByIDDTO(GetByIDBaseDTO):
    agency_id: int

    def get_where_mapping(self):
        return {
            "data_source_id": int(self.resource_id),
            "agency_id": int(self.agency_id),
        }


class AgenciesGetManyDTO(GetManyBaseDTO):
    approval_status: Optional[ApprovalStatus] = None
